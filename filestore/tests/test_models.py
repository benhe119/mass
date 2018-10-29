from pathlib import Path
import shutil
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db.utils import IntegrityError
from django.test import TransactionTestCase
from filestore.models import Settings, File, Folder


class FileTests(TransactionTestCase):

    def setUp(self):
        bash_macosx = File()
        bash_macosx.file_obj = SimpleUploadedFile(
            name='bash_macosx_x86_64',
            content=open('filestore/examples/bash_macosx_x86_64', 'rb').read(),
            content_type='application/octet-stream')
        bash_macosx.save()

    @classmethod
    def tearDown(cls):
        """Delete all File objects after each test, not necessarily needed for every test case"""
        for obj in File.objects.all():
            # required because test_delete_file already deleted the file
            try:
                obj.delete()
            except FileNotFoundError:
                pass

    def test_new_file(self):
        """Add a file with known properties to test adding a new File"""
        bash_macosx = File.objects.get(file_name='bash_macosx_x86_64')
        self.assertEqual(bash_macosx.size, 626272)
        self.assertEqual(bash_macosx.md5, '6e09e44ec1119410c999544ab9033dab')
        self.assertEqual(bash_macosx.sha1, '87e8300692a35010af8478978fab1ac4888114e1')
        self.assertEqual(bash_macosx.sha256, '295fbc2356e8605e804f95cb6d6f992335e247dbf11767fe8781e2a7f889978a')
        self.assertIn('Mach-O 64-bit x86_64 executable', bash_macosx.file_type)
        path = Path(bash_macosx.file_obj.path)
        self.assertTrue(path.parent.is_dir())
        self.assertTrue(path.is_file())

    def test_delete_file(self):
        """Delete a File object"""
        bash_macosx = File.objects.get(file_name='bash_macosx_x86_64')
        path = Path(bash_macosx.file_obj.path)
        bash_macosx.delete()
        self.assertFalse(path.exists())

    def test_duplicate_file(self):
        """A file with same SHA256 is not allowed"""
        bash_macosx_dup = File()
        bash_macosx_dup.file_obj = SimpleUploadedFile(
            name='bash_macosx_x86_64',
            content=open('filestore/examples/bash_macosx_x86_64', 'rb').read(),
            content_type='application/octet-stream')
        with self.assertRaises(IntegrityError):
            bash_macosx_dup.save()

    def test_delete_nonexistant_file(self):
        File.objects.create(file_obj=SimpleUploadedFile(
            name='file1', content=b'1234', content_type='application/octet-stream'))
        file1 = File.objects.get(file_name='file1')
        shutil.rmtree('/'.join(file1.path.split('/')[0:2]))
        file1.delete()

    def test_member_files(self):
        File.objects.create(file_obj=SimpleUploadedFile(
            name='some_other_txt_files.tar',
            content=open('filestore/examples/some_other_txt_files.tar', 'rb').read(),
            content_type='application/octet-stream')
        )
        source_file = File.objects.get(file_name='some_other_txt_files.tar')
        self.assertEqual(source_file.member_files_count, 2)


class ClamAVTests(TransactionTestCase):

    def test_clamav_file(self):
        """ClamAV should hit on the test EICAR file"""
        eicar = File()
        eicar.file_obj = SimpleUploadedFile(
            name='eicar.com.txt',
            content=open('filestore/examples/eicar.com.txt', 'rb').read(),
            content_type='application/octet-stream')
        eicar.save()
        eicar.refresh_from_db()
        self.assertEqual(eicar.clamav_msg, 'Eicar-Test-Signature')

    def test_clamav_disabled(self):
        """There should be no clamav_msg when it's disabled"""
        settings = Settings.load()
        settings.clamav_enabled = False
        settings.save()
        eicar = File()
        eicar.file_obj = SimpleUploadedFile(
            name='eicar.com.txt',
            content=open('filestore/examples/eicar.com.txt', 'rb').read(),
            content_type='application/octet-stream')
        eicar.save()
        eicar.refresh_from_db()
        self.assertEqual(eicar.clamav_msg, '')
        settings = Settings.load()
        settings.clamav_enabled = True
        settings.save()


class FolderTests(TransactionTestCase):

    def test_new_folder_nonexistant_path(self):
        """A Folder with a path that doesn't exist should not be added"""
        folder = Folder()
        folder.path = '/some/path'
        with self.assertRaises(ValidationError):
            folder.save()
        folders = Folder.objects.filter(path='/some/path')
        self.assertEqual(len(folders), 0)
