from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from django.template.loader import render_to_string
from django.urls import reverse_lazy
from django.views.generic import DetailView, ListView
from django.views.generic.edit import CreateView, DeleteView
from .models import File, Folder
from .tasks import extract_pcap, scan_folder


class FileList(ListView):
    model = File
    context_object_name = 'files'


class FileCreate(CreateView):
    model = File
    fields = ('file_obj', )
    success_url = reverse_lazy('file-list')


class FileDelete(DeleteView):
    model = File
    slug_field = 'sha256'
    success_url = reverse_lazy('file-list')


class FileDetail(DetailView):
    model = File
    slug_field = 'sha256'


class FolderList(ListView):
    model = Folder
    context_object_name = 'folders'


class FolderCreate(CreateView):
    model = Folder
    fields = ('path', 'recursive', )
    success_url = reverse_lazy('folder-list')


class FolderDelete(DeleteView):
    model = Folder
    success_url = reverse_lazy('folder-list')


class FolderDetail(DetailView):
    model = Folder
