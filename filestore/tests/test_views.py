from unittest import skipIf
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, TransactionTestCase
from django.urls import reverse
from filestore.models import File, Folder


class FileViewTests(TestCase):

    @classmethod
    def tearDown(cls):
        """Delete all File objects after each test, not necessarily needed for every test case"""
        for obj in File.objects.all():
            # required because test_delete_file already deleted the file
            try:
                obj.delete()
            except FileNotFoundError:
                pass

    def test_file_list_view(self):
        resp = self.client.get(reverse('file-list'))
        self.assertEqual(resp.status_code, 200)

    def test_file_add_view_error(self):
        """Shouldn't be able to create a File record without uploading a file"""
        resp = self.client.post(reverse('file-create'), {'file_obj': None})
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'errorlist')

    def test_file_add_delete_view_success(self):
        file_obj = SimpleUploadedFile(
            name='bash_macosx_x86_64',
            content=open('filestore/examples/bash_macosx_x86_64', 'rb').read(),
            content_type='application/octet-stream')
        resp = self.client.post(reverse('file-create'), {'file_obj': file_obj})
        self.assertEqual(resp.status_code, 302)
        file_rec = File.objects.get(pk=1)
        resp = self.client.post(reverse('file-delete', args=(file_rec.sha256,)))
        with self.assertRaises(File.DoesNotExist):
            File.objects.get(pk=1)

    def test_file_delete_multiple_success(self):
        """Test deleting 1 of 2 File records using checkboxes"""
        File.objects.create(file_obj=SimpleUploadedFile(
            name='file1', content=b'1234', content_type='application/octet-stream'))
        File.objects.create(file_obj=SimpleUploadedFile(
            name='file2', content=b'5678', content_type='application/octet-stream'))
        resp = self.client.post(reverse('file-list'), {'selected_files': ['1']})
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(File.objects.count(), 1)

    def test_file_delete_multiple_failure(self):
        """Clicking delete when no file checkboxes are selected should fail"""
        File.objects.create(file_obj=SimpleUploadedFile(
            name='file1', content=b'1234', content_type='application/octet-stream'))
        File.objects.create(file_obj=SimpleUploadedFile(
            name='file2', content=b'5678', content_type='application/octet-stream'))
        resp = self.client.post(reverse('file-list'), {'selected_files': []})
        self.assertContains(resp, 'errorlist')
        self.assertEqual(File.objects.count(), 2)

    @skipIf(settings.TESTING, 'skip tests that require bro')
    def test_file_add_pcap(self):
        """Test uploading a PCAP that should be extracted by bro"""
        pcap = SimpleUploadedFile(
            name='10_ben_pe32.pcap',
            content=open('filestore/examples/10_ben_pe32.pcap', 'rb').read(),
            content_type='application/octet-stream')
        resp = self.client.post(reverse('file-create'), {'file_obj': pcap})
        self.assertEqual(resp.status_code, 302)
        # TODO: make sure the correct File records are added

    def test_file_archive_extraction(self):
        archive = SimpleUploadedFile(
            name='some_txt_files.tar.gz',
            content=open('filestore/examples/some_txt_files.tar.gz', 'rb').read(),
            content_type='application/octet-stream')
        resp = self.client.post(reverse('file-create'), {'file_obj': archive})
        self.assertEqual(resp.status_code, 302)


class FileViewTransactionTests(TransactionTestCase):

    def test_file_upload_duplicate(self):
        orig_file = SimpleUploadedFile(name='file2', content=b'1234', content_type='application/octet-stream')
        resp = self.client.post(reverse('file-create'), {'file_obj': orig_file})
        dup_file = SimpleUploadedFile(name='file2', content=b'1234', content_type='application/octet-stream')
        resp = self.client.post(reverse('file-create'), {'file_obj': dup_file})
        self.assertContains(resp, 'errorlist')
        self.assertEqual(File.objects.count(), 1)


class FolderViewTests(TestCase):

    @classmethod
    def tearDown(self):
        """Delete all File objects after each test, not necessarily needed for every test case"""
        for obj in File.objects.all():
            # required because test_delete_file already deleted the file
            try:
                obj.delete()
            except FileNotFoundError:
                pass

    def test_folder_list_view(self):
        resp = self.client.get(reverse('folder-list'))
        self.assertEqual(resp.status_code, 200)

    def test_folder_add_view_empty_path(self):
        """Shouldn't be able to create a Folder record with no path"""
        self.client.post(reverse('folder-create'), {'path': None})
        self.assertEqual(Folder.objects.count(), 0)

    def test_folder_add_view_nonexistant_path(self):
        """Shouldn't be able to create a Folder record a non-existant path"""
        self.client.post(reverse('folder-create'), {'path': '/some/path'})
        self.assertEqual(Folder.objects.count(), 0)

    def test_folder_add_view_non_recursive_success(self):
        """Test creation of a non-recursive Folder"""
        path = 'filestore/tests/data'
        resp = self.client.post(
            reverse('folder-create'), {'path': path})
        self.assertEqual(resp.status_code, 302)
        folder = Folder.objects.get(path=path)
        self.assertEqual(folder.num_files, 1)

    def test_folder_add_view_recursive_success(self):
        """Test creation of a recursive Folder"""
        path = 'filestore/tests/data'
        resp = self.client.post(
            reverse('folder-create'), {'path': path, 'recursive': True})
        self.assertEqual(resp.status_code, 302)
        folder = Folder.objects.get(path=path)
        self.assertEqual(folder.num_files, 2)

    def test_file_delete_multiple_success(self):
        """Test deleting 1 of 2 Folder records using checkboxes"""
        Folder.objects.create(path='filestore/tests/data', recursive=False)
        Folder.objects.create(path='filestore/tests/data/sub_dir', recursive=False)
        resp = self.client.post(reverse('folder-list'), {'selected_folders': ['1']})
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(Folder.objects.count(), 1)

    def test_folder_delete_multiple_failure(self):
        """Clicking delete when no file checkboxes are selected should fail"""
        Folder.objects.create(path='filestore/tests/data', recursive=False)
        Folder.objects.create(path='filestore/tests/data/sub_dir', recursive=False)
        resp = self.client.post(reverse('folder-list'), {'selected_folders': []})
        self.assertContains(resp, 'errorlist')
        self.assertEqual(Folder.objects.count(), 2)
