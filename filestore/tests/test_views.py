from unittest import skipIf
from django.conf import settings
from django.db.utils import IntegrityError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse
from filestore.models import File, Folder

# TODO: improve views.py and tasks.py coverage
# TODO: reduce reliance on files already present, i.e. create and delete
#       files/folders in the tests
class FileViewTests(TestCase):

    def test_file_list_view(self):
        resp = self.client.get('/')
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

    def test_file_add_duplicate_file(self):
        bash_macosx = File()
        bash_macosx.file_obj = SimpleUploadedFile(
            name='bash_macosx_x86_64',
            content=open('filestore/examples/bash_macosx_x86_64', 'rb').read(),
            content_type='application/octet-stream')
        bash_macosx.save()
        bash_macosx_dup = File()
        bash_macosx_dup.file_obj = SimpleUploadedFile(
            name='bash_macosx_x86_64',
            content=open('filestore/examples/bash_macosx_x86_64', 'rb').read(),
            content_type='application/octet-stream')
        with self.assertRaises(IntegrityError):
            bash_macosx_dup.save()

    @skipIf(settings.TESTING, 'skip tests that require bro')
    def test_file_add_pcap(self):
        pcap = SimpleUploadedFile(
            name='10_ben_pe32.pcap',
            content=open('filestore/examples/10_ben_pe32.pcap', 'rb').read(),
            content_type='application/octet-stream')
        resp = self.client.post(reverse('file-create'), {'file_obj': pcap})
        self.assertEqual(resp.status_code, 302)


class FolderViewTests(TestCase):

    def test_folder_list_view(self):
        resp = self.client.get('/folders')
        self.assertEqual(resp.status_code, 301)

    def test_folder_add_view_empty_path(self):
        resp = self.client.post(reverse('folder-create'))
        self.assertContains(resp, '<ul class="errorlist"><li>This field is required.</li></ul>')
        self.assertEqual(Folder.objects.count(), 0)

    def test_folder_add_view_nonexistant_path(self):
        resp = self.client.post(
            reverse('folder-create'), {'path': '/some/path'})
        self.assertContains(resp, '<ul class="errorlist nonfield"><li>/some/path does not exist</li></ul>')
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
