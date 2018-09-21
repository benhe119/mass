from django.db.utils import IntegrityError
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views.generic import DetailView
from django.views.generic.edit import CreateView, DeleteView, FormView
from .forms import FileListForm, FolderListForm, ClamAVSettingsForm
from .models import File, Folder
from .tasks import extract_file, scan_folder # noqa


class FileList(FormView):
    model = File
    form_class = FileListForm
    template_name = 'filestore/file_list.html'

    @staticmethod
    def get_queryset():
        return File.objects.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['files'] = self.get_queryset()
        context['form'] = self.get_form(self.form_class)
        return context

    def post(self, request, *args, **kwargs):
        # TODO: add confirmation modal
        # selected_files is a list of checkboxes selected
        selected_files = request.POST.getlist('selected_files')
        form = self.get_form(self.form_class)
        # Return the form if no Files are selected (error added by FileListForm)
        if not selected_files:
            return render(request, self.template_name, {'form': form, 'files': self.get_queryset()})
        # Can't use bulk delete, need File.delete() to run to clean up files
        for obj in File.objects.filter(pk__in=request.POST.getlist('selected_files')):
            obj.delete()
        return redirect(reverse_lazy('file-list'))


class FileCreate(CreateView):
    model = File
    fields = ('file_obj', )
    success_url = reverse_lazy('file-list')

    def form_valid(self, form):
        try:
            return super().form_valid(form)
        except IntegrityError:
            form.add_error(None, 'Duplicate file')
            return self.form_invalid(form)


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

    @staticmethod
    def get_queryset():
        return Folder.objects.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['folders'] = self.get_queryset()
        context['form'] = self.get_form(self.form_class)
        return context

    def post(self, request, *args, **kwargs):
        # TODO: add confirmation modal
        selected_folders = request.POST.getlist('selected_folders')
        form = self.get_form(self.form_class)
        if not selected_folders:
            return render(request, self.template_name, {'form': form, 'folders': self.get_queryset()})
        # TODO: probably can replace this with bulk delete
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


def clamav_settings(request):
    form = ClamAVSettingsForm(request.POST or None)

    if request.method == 'POST':
        if form.is_valid():
            form.save()
        else:
            return HttpResponse('Error!')

    context = {'form': form}

    return render(request, 'filestore/clamav_settings.html', context)
