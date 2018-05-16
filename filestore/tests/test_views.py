import json
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse
from filestore.models import File, Folder


class FileViewTests(TestCase):

    def test_file_list_view(self):
        resp = self.client.get('/')
        self.assertEqual(resp.status_code, 200)

    def test_file_add_view_error(self):
        resp = self.client.post(reverse('file-create'), {'file_obj': None})

    def test_file_add_delete_view_success(self):
        file = SimpleUploadedFile(
            name='bash_macosx_x86_64',
            content=open('filestore/examples/bash_macosx_x86_64', 'rb').read(),
            content_type='application/octet-stream')
        resp = self.client.post(reverse('file-create'), {'file_obj': file})
        file = File.objects.get(pk=1)
        resp = self.client.post(reverse('file-delete', args=(file.sha256,)))

    def test_file_add_pcap(self):
        pcap = SimpleUploadedFile(
            name='10_ben_pe32.pcap',
            content=open('filestore/examples/10_ben_pe32.pcap', 'rb').read(),
            content_type='application/octet-stream')
        resp = self.client.post(reverse('file-create'), {'file_obj': pcap})


class FolderViewTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        pass

    def test_folder_list_view(self):
        resp = self.client.get('/folders')
        self.assertEqual(resp.status_code, 301)

    def test_folder_add_view_empty_path(self):
        resp = self.client.post(reverse('folder-create'))

    def test_folder_add_view_nonexistant_path(self):
        resp = self.client.post(
            reverse('folder-create'), {'path': '/some/path'})

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
