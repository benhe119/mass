from __future__ import absolute_import, unicode_literals
import logging
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
from django.conf import settings
from django.db import IntegrityError, transaction
from django.db.models.signals import post_save
from django.core.files import File as _File
from django.dispatch import receiver
import django_rq
from filestore.models import File, Folder

LOG = logging.getLogger(__name__)
q = django_rq.get_queue('default')


def scan_folder(instance):
    path = Path(instance.path)
    LOG.info('Scanning %s', path)

    # Adjust glob method based on recursive preference
    if instance.recursive:
        glob = path.rglob('*')
    else:
        glob = path.glob('*')

    # Loop over files, exclude files that are read protected and
    #   handle duplicates
    num_files = 0
    num_duplicates = 0
    for f in glob:
        if f.is_file():
            file_rec = File()
            num_files += 1
            try:
                _file = open(f, 'rb')
            except PermissionError:
                LOG.warning('Permission denied: %s', file_rec)
                break
            file_rec.file_obj = _File(_file)
            # Don't add duplicates files (based on SHA256)
            try:
                with transaction.atomic():
                    file_rec.save()
                LOG.info('Saved new file: %s %s', file_rec, file_rec.sha256)
            except IntegrityError:
                LOG.info('%s %s already exists', file_rec, file_rec.sha256)
                # Update counters
                num_duplicates += 1

    num_files_added = num_files - num_duplicates
    LOG.info('Found %s, added %s, skipped %s duplicates', num_files, num_files, num_duplicates)
    instance.num_files = num_files_added
    if instance.temporary:
        # Currently only used when bro extracts a PCAP
        LOG.info('%s is temporary, deleting', instance.path)
        instance.delete()
    else:
        instance.save()


@receiver(post_save, sender=Folder)
def scan_folder_handler(sender, instance, created, **kwargs):
    # Only run job for new Folders
    if created:
        q.enqueue(scan_folder, instance)


def extract_file(instance, pcap=False, archive=False):
    if pcap:
        try:
            subprocess.run(['which', 'bro'], check=True)
        except subprocess.CalledProcessError:
            LOG.error('Cannot find bro')
            raise
        LOG.info('Extacting PCAP %s', instance.path)
        shutil.rmtree('bro/tmp', ignore_errors=True)
        os.mkdir('bro/tmp')
        extract_cmd_str = f'bro -C -r ../../{instance.path} ../plugins/extract-all-files.bro'
        subprocess.run(extract_cmd_str, shell=True, cwd='bro/tmp')
        Folder.objects.create(path='bro/tmp/extract_files', temporary=True)

    if archive:
        temp_dir = tempfile.mkdtemp()
        LOG.info('Extracting %s to %s', instance.path, temp_dir)
        extract_cmd = f'7z x {instance.path} -aoa -o{temp_dir}'
        LOG.info('Extraction Command: %s', extract_cmd)
        subprocess.run(extract_cmd, shell=True)
        Folder.objects.create(path=temp_dir, recursive=True, temporary=True)


@receiver(post_save, sender=File)
def extract_file_handler(sender, instance, created, **kwargs):
    # Only run job for new Files that have been typed
    if created and instance.file_type is not None:
        for pcap_str in settings.PCAP_STRINGS:
            if pcap_str in instance.file_type:
                q.enqueue(extract_file, instance, pcap=True)
                break
        for archive_type in settings.ARCHIVE_TYPES:
            if archive_type in instance.file_type.lower():
                q.enqueue(extract_file, instance, archive=True)
                break
