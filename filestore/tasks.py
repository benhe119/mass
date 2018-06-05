from __future__ import absolute_import, unicode_literals
import logging
from pathlib import Path
import subprocess
from django.conf import settings
from django.db import IntegrityError, transaction
from django.db.models.signals import post_save
from django.core.files import File as _File
from django.dispatch import receiver
import django_rq
from filestore.models import File, Folder

logger = logging.getLogger(__name__)
q = django_rq.get_queue('default')


def scan_folder(instance):
    path = Path(instance.path)
    file_recs = []
    if instance.recursive:
        glob = path.rglob('*')
    else:
        glob = path.glob('*')
    for f in glob:
        file_rec = File()
        try:
            if f.is_file():
                _file = open(f, 'rb')
                file_rec.file_obj = _File(_file)
                file_recs.append(file_rec)
        except PermissionError:
            logger.warning(f'Permission denied: "{f}"')

    num_files = len(file_recs)
    num_files_added = num_files
    num_duplicates = 0
    for file_rec in file_recs:
        try:
            with transaction.atomic():
                file_rec.save()
        except IntegrityError:
            logger.info(f'{file_rec} {file_rec.sha256} already exists')
            num_files_added -= 1
            num_duplicates += 1
    logger.info(f'Found {num_files}, added {num_files_added}, skipped {num_duplicates} duplicates')
    instance.num_files = num_files_added
    if instance.temporary:
        logger.info(f'{instance.path} is temporary, deleting')
        instance.delete()
    else:
        instance.save()


@receiver(post_save, sender=Folder)
def scan_folder_handler(sender, instance, created, **kwargs):
    if created:
        q.enqueue(scan_folder, instance)


def extract_pcap(instance):
    print('Extacting', instance.path)
    extract_cmd_str = 'rm -rf bro/tmp && mkdir bro/tmp && cd bro/tmp && bro -C -r ../../{} ../plugins/extract-all-files.bro'.format(instance.path)
    extract_cmd = subprocess.run(extract_cmd_str, shell=True)
    new_folder = Folder.objects.create(path='bro/tmp/extract_files', temporary=True)


@receiver(post_save, sender=File)
def extract_pcap_handler(sender, instance, created, **kwargs):
    if created and instance.file_type is not None:
        for pcap_str in settings.PCAP_STRINGS:
            if pcap_str in instance.file_type:
                print('found PCAP')
                q.enqueue(extract_pcap, instance)
                break
