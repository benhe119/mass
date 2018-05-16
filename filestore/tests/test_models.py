from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db.utils import IntegrityError
from django.test import TestCase
from pathlib import Path
import shutil
from filestore.models import File, Folder


def rmdir(dir):
    for item in dir.iterdir():
        if item.is_dir():
            rmdir(item)
            item.rmdir()
        else:
            item.unlink()

class FileTests(TestCase):

    def setUp(self):
        bash_macosx = File()
        bash_macosx.file_obj = SimpleUploadedFile(
            name='bash_macosx_x86_64',
            content=open('filestore/examples/bash_macosx_x86_64', 'rb').read(),
            content_type='application/octet-stream')
        bash_macosx.save()

    def tearDown(self):
        rmdir(Path('files/'))

    def test_new_file(self):
        bash_macosx = File.objects.get(file_name='bash_macosx_x86_64')
        self.assertEqual(bash_macosx.size, 626272)
        self.assertEqual(
            bash_macosx.md5,
            '6e09e44ec1119410c999544ab9033dab')
        self.assertEqual(
            bash_macosx.sha1,
            '87e8300692a35010af8478978fab1ac4888114e1')
        self.assertEqual(
            bash_macosx.sha256,
            '295fbc2356e8605e804f95cb6d6f992335e247dbf11767fe8781e2a7f889978a')
        self.assertIn(
            'Mach-O 64-bit x86_64 executable',
            bash_macosx.file_type)
        path = Path(bash_macosx.file_obj.path)
        self.assertTrue(path.parent.is_dir())
        self.assertTrue(path.is_file())

    def test_delete_file(self):
        bash_macosx = File.objects.get(file_name='bash_macosx_x86_64')
        path = Path(bash_macosx.file_obj.path)
        bash_macosx.delete()
        with self.assertRaises(FileNotFoundError):
            path.stat()

    def test_duplicate_file(self):
        bash_macosx_dup = File()
        bash_macosx_dup.file_obj = SimpleUploadedFile(
            name='bash_macosx_x86_64',
            content=open('filestore/examples/bash_macosx_x86_64', 'rb').read(),
            content_type='application/octet-stream')
        with self.assertRaises(IntegrityError):
            bash_macosx_dup.save()


class FolderTests(TestCase):

    def test_new_folder_nonexistant_path(self):
        folder = Folder()
        folder.path = '/some/path'
        with self.assertRaises(ValidationError):
            folder.save()
        folders = Folder.objects.filter(path='/some/path')
        self.assertEqual(len(folders), 0)
