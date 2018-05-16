from __future__ import absolute_import, unicode_literals
from pathlib import Path
import subprocess
from django.db import IntegrityError, transaction
from django.db.models.signals import post_save
from django.conf import settings
from django.core.files import File as _File
from django.dispatch import receiver
from fakeredis import FakeStrictRedis
from redis import Redis
from rq import Queue
from filestore.models import File, Folder

if settings.TESTING:
    q = Queue(async=False, connection=FakeStrictRedis())
else:
    q = Queue(connection=Redis())

def scan_folder(instance):
    path = Path(instance.path)
    files = []
    if instance.recursive:
        for f in path.rglob('*'):
            try:
                if f.is_file():
                    files.append(f)
            except PermissionError:
                print('Permission denied', f)
    else:
        for f in path.glob('*'):
            try:
                if f.is_file():
                    files.append(f)
            except PermissionError:
                print('Permission denied', f)
    instance.num_files = len(files)
    for _file in files:
        file_rec = File()
        try:
            f = open(_file, 'rb')
        except PermissionError:
            print('Cannot open', _file)
            continue
        file_rec.file_obj = _File(f)
        try:
            with transaction.atomic():
                file_rec.save()
            instance.num_files_added += 1
        except IntegrityError:
            print(f, 'already exists')
            continue
    print('Found', instance.num_files, 'added', instance.num_files_added)
    instance.save()

@receiver(post_save, sender=Folder)
def scan_folder_handler(sender, instance, created, **kwargs):
    if created:
        q.enqueue(scan_folder, instance)

def extract_pcap(instance):
    print('Extacting', instance.path)
    extract_cmd_str = 'rm -rf bro/tmp && mkdir bro/tmp && cd bro/tmp && bro -C -r ../../{} ../plugins/extract-all-files.bro'.format(instance.path)
    extract_cmd = subprocess.run(extract_cmd_str, shell=True)
    print(extract_cmd_str)

@receiver(post_save, sender=File)
def extract_pcap_handler(sender, instance, created, **kwargs):
    if created and instance.file_type is not None:
        if 'tcpdump' in instance.file_type:
            q.enqueue(extract_pcap, instance)
