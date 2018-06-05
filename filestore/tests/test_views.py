from unittest import skipIf
from django.conf import settings
from django.db.utils import IntegrityError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse
from filestore.models import File, Folder


class FileViewTests(TestCase):

    @classmethod
    def tearDown(self):
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
        resp = self.client.post(reverse('file-create'), {'file_obj': None})
        self.assertEqual(resp.status_code, 200)

    def test_file_add_delete_view_success(self):
        file = SimpleUploadedFile(
            name='bash_macosx_x86_64',
            content=open('filestore/examples/bash_macosx_x86_64', 'rb').read(),
            content_type='application/octet-stream')
        resp = self.client.post(reverse('file-create'), {'file_obj': file})
        self.assertEqual(resp.status_code, 302)
        file = File.objects.get(pk=1)
        resp = self.client.post(reverse('file-delete', args=(file.sha256,)))
        with self.assertRaises(File.DoesNotExist):
            File.objects.get(pk=1)

    def test_file_delete_multiple_success(self):
        File.objects.create(file_obj=SimpleUploadedFile(
            name='file1',
            content=b'1234', content_type='application/octet-stream'))
        File.objects.create(file_obj=SimpleUploadedFile(
            name='file2',
            content=b'5678', content_type='application/octet-stream'))
        resp = self.client.post(reverse('file-list'), {'selected_files': ['1']})
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(File.objects.count(), 1)

    def test_file_delete_multiple_failure(self):
        File.objects.create(file_obj=SimpleUploadedFile(
            name='file1',
            content=b'1234', content_type='application/octet-stream'))
        File.objects.create(file_obj=SimpleUploadedFile(
            name='file2',
            content=b'5678', content_type='application/octet-stream'))
        resp = self.client.post(reverse('file-list'), {'selected_files': []})
        self.assertContains(resp, 'errorlist')
        self.assertEqual(File.objects.count(), 2)

    @skipIf(settings.TESTING, 'skip tests that require bro')
    def test_file_add_pcap(self):
        pcap = SimpleUploadedFile(
            name='10_ben_pe32.pcap',
            content=open('filestore/examples/10_ben_pe32.pcap', 'rb').read(),
            content_type='application/octet-stream')
        resp = self.client.post(reverse('file-create'), {'file_obj': pcap})
        self.assertEqual(resp.status_code, 302)


class FolderViewTests(TestCase):

    @classmethod
    def tearDown(self):
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
        resp = self.client.post(reverse('folder-create'))
        self.assertEqual(Folder.objects.count(), 0)

    def test_folder_add_view_nonexistant_path(self):
        resp = self.client.post(
            reverse('folder-create'), {'path': '/some/path'})
        self.assertEqual(Folder.objects.count(), 0)

    def test_folder_add_view_non_recursive_success(self):
        path = 'filestore/tests/data'
        resp = self.client.post(
            reverse('folder-create'), {'path': path})
        self.assertEqual(resp.status_code, 302)
        folder = Folder.objects.get(path=path)
        self.assertEqual(folder.num_files, 1)

    def test_folder_add_view_recursive_success(self):
        path = 'filestore/tests/data'
        resp = self.client.post(
            reverse('folder-create'), {'path': path, 'recursive': True})
        self.assertEqual(resp.status_code, 302)
        folder = Folder.objects.get(path=path)
        self.assertEqual(folder.num_files, 2)

    def test_file_delete_multiple_success(self):
        Folder.objects.create(path='filestore/tests/data', recursive=False)
        Folder.objects.create(path='filestore/tests/data/sub_dir', recursive=False)
        resp = self.client.post(reverse('folder-list'), {'selected_folders': ['1']})
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(Folder.objects.count(), 1)

    def test_folder_delete_multiple_failure(self):
        Folder.objects.create(path='filestore/tests/data', recursive=False)
        Folder.objects.create(path='filestore/tests/data/sub_dir', recursive=False)
        resp = self.client.post(reverse('folder-list'), {'selected_folders': []})
        self.assertContains(resp, 'errorlist')
        self.assertEqual(Folder.objects.count(), 2)
