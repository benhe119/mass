from datetime import datetime as dt
import hashlib
from pathlib import Path
from django.core.exceptions import ValidationError
from django.db import models
from django.urls import reverse
import magic


def get_upload_path(instance, filename):
    return 'files/{}/{}/{}'.format(
        instance.sha256[0:2], instance.sha256[2:4], instance.sha256)


class File(models.Model):
    file_obj = models.FileField(upload_to=get_upload_path, editable=True)
    file_name = models.CharField(max_length=250, editable=False)
    file_type = models.CharField(max_length=100, editable=False, null=True)
    path = models.CharField(max_length=250, editable=False)
    size = models.PositiveIntegerField(editable=False, default=0)
    md5 = models.CharField(max_length=32, editable=False, unique=True)
    sha1 = models.CharField(max_length=40, editable=False, unique=True)
    sha256 = models.CharField(max_length=64, editable=False, unique=True)
    added = models.DateTimeField(auto_now_add=True)
    time_to_process = models.PositiveIntegerField(editable=False, default=0)

    def save(self, *args, **kwargs):
        created = self.pk is None
        if created:
            self.file_name = Path(self.file_obj.name).name
            self.size = self.file_obj.size
            file_handle = self.file_obj.file
            _proc_start = dt.now()
            self.md5, self.sha1, self.sha256, self.file_type = self.get_file_info(file_handle)
            self.time_to_process = int((dt.now() - _proc_start).total_seconds() * 1000)
            self.path = get_upload_path(self, None)
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        path = Path(self.file_obj.path)
        try:
            path.unlink()
            path.parent.rmdir()
        except FileNotFoundError:
            pass
        finally:
            super().delete(*args, **kwargs)

    @staticmethod
    def get_file_info(file_obj):
        file_obj.seek(0)
        md5 = hashlib.md5()
        sha1 = hashlib.sha1()
        sha256 = hashlib.sha256()
        file_type = None
        idx = 0
        file_type = None
        for chunk in iter(lambda: file_obj.read(4096), b''):
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
    path = models.CharField(max_length=250)
    num_files = models.PositiveIntegerField(editable=False, default=0)
    num_files_added = models.PositiveIntegerField(editable=False, default=0)
    recursive = models.BooleanField(default=False)
    temporary = models.BooleanField(default=False, editable=False)

    class Meta:
        unique_together = (('path', 'recursive'),)

    def clean(self):
        if not Path(self.path).exists():
            raise ValidationError('{} does not exist'.format(self.path))

    def save(self, *args, **kwargs):
        created = self.pk is None
        if created:
            self.full_clean()
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('folder-detail', kwargs={'pk': self.pk})

    def __str__(self):
        return self.path
