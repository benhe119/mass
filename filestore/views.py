from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.utils import IntegrityError
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views.generic import DetailView
from django.views.generic.edit import CreateView, DeleteView, FormView, UpdateView
import django_rq
from .forms import SettingsForm, FileListForm, FolderListForm
from .models import Settings, File, Folder
from .tasks import extract_file, scan_folder, update_clamav # noqa

q = django_rq.get_queue('default')


def index(request):
    return redirect(reverse_lazy('file-list'))


class FileList(FormView):
    model = File
    form_class = FileListForm
    template_name = 'filestore/file_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        file_list = File.objects.all()
        paginator = Paginator(file_list, 25)
        page = self.request.GET.get('page', 1)
        try:
            context['files'] = paginator.page(page)
        except PageNotAnInteger:
            context['files'] = paginator.page(1)
        except EmptyPage:
            context['files'] = paginator.page(paginator.num_pages)
        context['form'] = self.get_form(self.form_class)
        return context

    def post(self, request, *args, **kwargs):
        # selected_files is a list of checkboxes selected
        selected_files = request.POST.getlist('selected_files')
        form = self.get_form(self.form_class)
        # Return the form if no Files are selected (error added by FileListForm)
        if not selected_files:
            return render(request, self.template_name, {'form': form})
        # Can't use bulk delete, need File.delete() to run to clean up files
        for obj in File.objects.filter(pk__in=request.POST.getlist('selected_files')):
            obj.delete()
        return redirect(reverse_lazy('file-list'))


class FileCreate(SuccessMessageMixin, CreateView):
    model = File
    fields = ('file_obj', )
    success_message = '"%(file_name)s" was added'
    success_url = reverse_lazy('file-list')

    def form_valid(self, form):
        try:
            return super().form_valid(form)
        except IntegrityError:
            form.add_error(None, 'Duplicate file')
            return self.form_invalid(form)

    def get_success_message(self, cleaned_data):
        return self.success_message % dict(
            cleaned_data, file_name=self.object.file_name,
        )


class FileDelete(SuccessMessageMixin, DeleteView):
    model = File
    slug_field = 'sha256'
    success_message = '"%(file_name)s" was deleted'
    success_url = reverse_lazy('file-list')

    def delete(self, request, *args, **kwargs):
        obj = self.get_object()
        messages.success(self.request, self.success_message % obj.__dict__)
        return super(FileDelete, self).delete(request, *args, **kwargs)


class FileDetail(DetailView):
    model = File
    slug_field = 'sha256'


class FolderList(FormView):
    model = Folder
    form_class = FolderListForm
    template_name = 'filestore/folder_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        folder_list = Folder.objects.all()
        paginator = Paginator(folder_list, 25)
        page = self.request.GET.get('page', 1)
        try:
            context['folders'] = paginator.page(page)
        except PageNotAnInteger:
            context['folders'] = paginator.page(1)
        except EmptyPage:
            context['folders'] = paginator.page(paginator.num_pages)
        context['form'] = self.get_form(self.form_class)
        return context

    def post(self, request, *args, **kwargs):
        # selected_folders is a list of checkboxes selected
        selected_folders = request.POST.getlist('selected_folders')
        form = self.get_form(self.form_class)
        # Return the form if no Folders are selected (error added by FolderListForm)
        if not selected_folders:
            return render(request, self.template_name, {'form': form})
        # Delete the Folder records one at a time
        for obj in Folder.objects.filter(pk__in=request.POST.getlist('selected_folders')):
            obj.delete()
        return redirect(reverse_lazy('folder-list'))


class FolderCreate(SuccessMessageMixin, CreateView):
    model = Folder
    fields = ('path', 'recursive', )
    success_message = '"%(path)s" was added'
    success_url = reverse_lazy('folder-list')

    def get_success_message(self, cleaned_data):
        return self.success_message % dict(
            cleaned_data, file_name=self.object.path,
        )


class FolderDelete(SuccessMessageMixin, DeleteView):
    model = Folder
    success_url = reverse_lazy('folder-list')


class FolderDetail(DetailView):
    model = Folder


class SettingsUpdate(SuccessMessageMixin, UpdateView):
    model = Settings
    slug_field = 'name'
    form_class = SettingsForm
    success_message = 'Settings saved'

    @staticmethod
    def get_queryset():
        return Settings.objects.filter(pk=1)


def update_clamav_db(request):
    q.enqueue(update_clamav)
    messages.success(request, 'Updated ClamAV Signature Database')
    return redirect(reverse_lazy('settings', kwargs={'slug': 'main'}))
