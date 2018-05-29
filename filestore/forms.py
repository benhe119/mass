from django import forms
from .models import File, Folder


class FileListForm(forms.Form):

    selected_files = forms.MultipleChoiceField(
        widget=forms.CheckboxSelectMultiple,
        required=False
    )

    class Meta:
        model = File
        fields = ('selected_files',)


class FolderListForm(forms.Form):

    selected_folders = forms.MultipleChoiceField(
        widget=forms.CheckboxSelectMultiple,
        required=False
    )

    class Meta:
        model = Folder
        fields = ('selected_folders',)
