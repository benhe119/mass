from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import DetailView, ListView
from django.views.generic.edit import CreateView, DeleteView
from .forms import FileListForm, FolderListForm
from .models import File, Folder
from .tasks import extract_pcap, scan_folder


class FileList(ListView):
    model = File
    context_object_name = 'files'
    form_class = FileListForm
    object_list = File.objects.all()
    template_name = 'filestore/file_list.html'

    def get_queryset(self):
        return File.objects.all()

    def get_context_data(self, **kwargs):
        return super().get_context_data(**kwargs)

    def post(self, request, *args, **kwargs):
        for obj in File.objects.filter(pk__in=request.POST.getlist('selected_files')):
            obj.delete()
        return render(request, self.template_name, self.get_context_data())


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
    form_class = FolderListForm
    object_list = Folder.objects.all()
    template_name = 'filestore/folder_list.html'

    def get_queryset(self):
        return Folder.objects.all()

    def get_context_data(self, **kwargs):
        return super().get_context_data(**kwargs)

    def post(self, request, *args, **kwargs):
        for obj in Folder.objects.filter(pk__in=request.POST.getlist('selected_folders')):
            obj.delete()
        return render(request, self.template_name, self.get_context_data())


class FolderCreate(CreateView):
    model = Folder
    fields = ('path', 'recursive', )
    success_url = reverse_lazy('folder-list')


class FolderDelete(DeleteView):
    model = Folder
    success_url = reverse_lazy('folder-list')


class FolderDetail(DetailView):
    model = Folder
