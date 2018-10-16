from datetime import datetime as dt
import hashlib
import logging
from pathlib import Path
from django.core.cache import cache
from django.core.exceptions import ValidationError
from django.db import models
from django.db.utils import IntegrityError
from django.urls import reverse
import pyclamd

LOG = logging.getLogger(__name__)

try:
    import magic
except ImportError:
    import sys
    LOG.error('ERROR: Cannot find magic library')
    # No real reason to continue without libmagic
    sys.exit(1)


def get_upload_path(instance, filename):
    """Keep the number of files in a directory low by slicing the SHA256"""
    return 'files/{}/{}/{}'.format(
        instance.sha256[0:2], instance.sha256[2:4], instance.sha256)


# TODO: make RQ job
def delete_file_empty_dirs(path, duplicate=False):
    """Delete file on disk and any empty directories"""
    path = Path(path)

    if duplicate:
        [f.unlink() for f in path.parent.glob('*_*')]
    else:
        [f.unlink() for f in path.parent.glob('*')]

    # Delete empty directories up to 2 ancestors, if files/ab/cd and files/ab are empty,
    #   they'll both be deleted. It goes 2 levels up following get_upload_path()
    deleted_dirs = []
    if sum(1 for f in path.parents[0].iterdir()) == 0:
        deleted_dirs.append(str(path.parents[0]))
        path.parents[0].rmdir()
        if sum(1 for f in path.parents[1].iterdir()) == 0:
            deleted_dirs.append(str(path.parents[1]))
            path.parents[1].rmdir()
    if deleted_dirs:
        deleted_dirs_str = ', '.join(deleted_dirs)
        LOG.info('Deleted empty directories %s', deleted_dirs_str)


class SettingsModel(models.Model):
    """Abstract class to handle settings as singletons, based on:
    https://steelkiwi.com/blog/practical-application-singleton-design-pattern/"""
    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        self.pk = 1
        super(SettingsModel, self).save(*args, **kwargs)
        self.set_cache()

    def delete(self, *args, **kwargs):
        pass

    def set_cache(self):
        cache.set(self.__class__.__name__, self)

    @classmethod
    def load(cls):
        # Check if the record is in the cache ...
        if cache.get(cls.__name__) is None:
            obj, created = cls.objects.get_or_create(pk=1)
            if not created:
                # ... it's not! so cache it
                obj.set_cache()
        return cache.get(cls.__name__)


class Settings(SettingsModel):
    name = models.CharField(max_length=25, editable=False)
    clamav_enabled = models.BooleanField(default=True)
    clamav_last_updated = models.DateTimeField(null=True)
    clamav_main_sigs = models.IntegerField(null=True)
    clamav_main_ver = models.IntegerField(null=True)
    clamav_daily_sigs = models.IntegerField(null=True)
    clamav_daily_ver = models.IntegerField(null=True)
    clamav_bytecode_sigs = models.IntegerField(null=True)
    clamav_bytecode_ver = models.IntegerField(null=True)

    def get_absolute_url(self):
        return reverse('settings', kwargs={'slug': 'main'})


class File(models.Model):
    """Record of files added, size, type, hashes and disk path"""
    file_obj = models.FileField(upload_to=get_upload_path, editable=True)
    file_name = models.CharField(max_length=250, editable=False)
    file_type = models.CharField(max_length=100, editable=False, null=True)
    path = models.CharField(max_length=250, editable=False)
    size = models.PositiveIntegerField(editable=False, default=0)
    md5 = models.CharField(max_length=32, editable=False, unique=True)
    sha1 = models.CharField(max_length=40, editable=False, unique=True)
    sha256 = models.CharField(max_length=64, editable=False, unique=True)
    clamav_msg = models.CharField(max_length=250, editable=False, default='')
    added = models.DateTimeField(auto_now_add=True)
    time_to_process = models.PositiveIntegerField(editable=False, default=0)

    def save(self, *args, **kwargs):
        if self.pk is None:
            # Set name and size of the file
            self.file_name = Path(self.file_obj.name).name
            self.size = self.file_obj.size
            _proc_start = dt.now()
            # Pass the file handle/pointer to calculate checksums and get filetype.
            #   This should be (much?) faster than using disk I/O
            self.md5, self.sha1, self.sha256, self.file_type = self.get_file_info(self.file_obj.file)
            # ClamAV has a default file size limit of 25 MB
            if Settings.load().clamav_enabled and self.size < 25000000:
                self.clamav_msg = self.clamav_scan(self.file_obj.file, self.file_name)
            self.time_to_process = int((dt.now() - _proc_start).total_seconds() * 1000)
            self.path = get_upload_path(self, None)
        try:
            super().save(*args, **kwargs)

        # Django's FileField writes the file to disk first, so if it's a duplicate
        #   it needs to be removed
        except IntegrityError:
            delete_file_empty_dirs(self.path, duplicate=True)
            raise

    def delete(self, *args, **kwargs):
        # Delete file and empty directories as well as the record
        try:
            delete_file_empty_dirs(self.path)
        except FileNotFoundError:
            LOG.warning('%s was not found, deleting record', self.path)
        finally:
            super().delete(*args, **kwargs)

    @staticmethod
    def _connect_clamd():
        try:
            return pyclamd.ClamdAgnostic()
        except ValueError:
            LOG.warning('Unable to connect to clamd')
            return None

    def clamav_scan(self, file_obj, file_name):
        cd = self._connect_clamd()
        if cd:
            # Go to the beginning of the file
            file_obj.seek(0)
            try:
                clam_results = cd.scan_stream(file_obj.read())
                if clam_results:
                    clamav_msg = clam_results['stream'][1]
                    LOG.info('ClamAV found "%s" in %s', clamav_msg, file_name)
                    return clamav_msg
                LOG.info('No ClamAV hits in %s', file_name)
                return ''
            except BrokenPipeError:
                LOG.warning('There was a problem scanning %s', file_name)
        else:
            return ''

    @staticmethod
    def get_file_info(file_obj):
        # Seek to the beginning of the file, upload process caused it to
        #   be read to the end.
        file_obj.seek(0)
        md5 = hashlib.md5()
        sha1 = hashlib.sha1()
        sha256 = hashlib.sha256()
        file_type = None
        idx = 0
        file_type = None
        for chunk in iter(lambda: file_obj.read(2**16), b''):
            # Only need to read the first chunk to determine the file type
            if idx == 0:
                with magic.Magic() as m:
                    file_type = m.id_buffer(chunk)
            idx += 1
            md5.update(chunk)
            sha1.update(chunk)
            sha256.update(chunk)
        return (md5.hexdigest(), sha1.hexdigest(), sha256.hexdigest(), file_type)

    def get_absolute_url(self):
        return reverse('file-detail', kwargs={'slug': self.sha256})

    def __str__(self):
        return '{} ({})'.format(self.file_name, self.file_type)


class Folder(models.Model):
    """Record of folders scanned"""
    path = models.CharField(max_length=250)
    num_files = models.PositiveIntegerField(editable=False, default=0)
    recursive = models.BooleanField(default=False)
    temporary = models.BooleanField(default=False, editable=False)

    class Meta:
        # Same path can be added as recursive and non-recursive
        unique_together = (('path', 'recursive'),)

    def clean(self):
        # Don't add paths that don't exist of the host system
        if not Path(self.path).exists():
            raise ValidationError('{} does not exist'.format(self.path))

    def save(self, *args, **kwargs):
        if self.pk is None:
            self.full_clean()
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('folder-detail', kwargs={'pk': self.pk})

    def __str__(self):
        return self.path
