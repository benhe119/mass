from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views.generic import DetailView, ListView
from django.views.generic.edit import CreateView, DeleteView, FormView
from .forms import FileListForm, FolderListForm
from .models import File, Folder
from .tasks import extract_pcap, scan_folder


class FileList(FormView):
    model = File
    form_class = FileListForm
    template_name = 'filestore/file_list.html'

    def get_queryset(self):
        return File.objects.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['files'] = self.get_queryset()
        context['form'] = self.get_form(self.form_class)
        return context

    def post(self, request, *args, **kwargs):
        selected_files = request.POST.getlist('selected_files')
        form = self.get_form(self.form_class)
        if not selected_files:
            return render(request, self.template_name, {'form': form, 'files': self.get_queryset()})
        else:
            for obj in File.objects.filter(pk__in=request.POST.getlist('selected_files')):
                obj.delete()
            return redirect(reverse_lazy('file-list'))


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


class FolderList(FormView):
    model = Folder
    form_class = FolderListForm
    template_name = 'filestore/folder_list.html'

    def get_queryset(self):
        return Folder.objects.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['folders'] = self.get_queryset()
        context['form'] = self.get_form(self.form_class)
        return context

    def post(self, request, *args, **kwargs):
        selected_folders = request.POST.getlist('selected_folders')
        form = self.get_form(self.form_class)
        if not selected_folders:
            return render(request, self.template_name, {'form': form, 'folders': self.get_queryset()})
        else:
            for obj in Folder.objects.filter(pk__in=request.POST.getlist('selected_folders')):
                obj.delete()
            return redirect(reverse_lazy('folder-list'))


class FolderCreate(CreateView):
    model = Folder
    fields = ('path', 'recursive', )
    success_url = reverse_lazy('folder-list')


class FolderDelete(DeleteView):
    model = Folder
    success_url = reverse_lazy('folder-list')


class FolderDetail(DetailView):
    model = Folder
