from __future__ import absolute_import, unicode_literals
import logging
from pathlib import Path
import subprocess
import tempfile
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
    logger.info(f'Scanning {path}')

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
                logger.warning(f'Permission denied: {file_rec}')
                break
            file_rec.file_obj = _File(_file)
            # Don't add duplicates files (based on SHA256)
            try:
                with transaction.atomic():
                    file_rec.save()
                logger.info(f'Saved new file: {file_rec} {file_rec.sha256}')
            except IntegrityError:
                logger.info(f'{file_rec} {file_rec.sha256} already exists')
                # Update counters
                num_duplicates += 1

    num_files_added = num_files - num_duplicates
    logger.info(f'Found {num_files}, added {num_files_added}, skipped {num_duplicates} duplicates')
    instance.num_files = num_files_added
    if instance.temporary:
        # Currently only used when bro extracts a PCAP
        logger.info(f'{instance.path} is temporary, deleting')
        instance.delete()
    else:
        instance.save()


@receiver(post_save, sender=Folder)
def scan_folder_handler(sender, instance, created, **kwargs):
    # Only run job for new Folders
    if created:
        q.enqueue(scan_folder, instance)


def extract_pcap(instance):
    # TODO: Use pathlib to handle directory interaction
    # raise exception if bro executable is not found, will cause job to be marked as failed
    try:
        subprocess.run(['which', 'bro'], check=True)
    except subprocess.CalledProcessError:
        logger.error('Cannot find bro')
        raise
    logger.info(f'Extacting PCAP {instance.path}')
    extract_cmd_str = 'rm -rf bro/tmp && mkdir bro/tmp && cd bro/tmp && bro -C -r ../../{} ../plugins/extract-all-files.bro'.format(instance.path)
    subprocess.run(extract_cmd_str, shell=True)
    Folder.objects.create(path='bro/tmp/extract_files', temporary=True)


@receiver(post_save, sender=File)
def extract_pcap_handler(sender, instance, created, **kwargs):
    # Only run job for new Files that have been typed
    if created and instance.file_type is not None:
        # TODO: has to be a more pythonic way to do this - any() maybe?
        for pcap_str in settings.PCAP_STRINGS:
            if pcap_str in instance.file_type:
                q.enqueue(extract_pcap, instance)
                break


def extract_archive(instance):
    temp_dir = tempfile.mkdtemp()
    logger.info(f'Extracting {instance.path} to {temp_dir}')
    extract_cmd = f'7z x {instance.path} -aoa -o{temp_dir}'
    logger.info(f'Extraction Command: {extract_cmd}')
    subprocess.run(extract_cmd, shell=True)
    Folder.objects.create(path=temp_dir, recursive=True, temporary=True)


@receiver(post_save, sender=File)
def extract_archive_handler(sender, instance, created, **kwargs):
    # Only run job for new Files that have been typed
    if created and instance.file_type is not None:
        for archive_type in settings.ARCHIVE_TYPES:
            if archive_type in instance.file_type.lower():
                q.enqueue(extract_archive, instance)
                break
