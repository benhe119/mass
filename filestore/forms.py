from django import forms
from .models import File, Folder

# TODO: add test_forms.py
class FileListForm(forms.ModelForm):

    selected_files = forms.MultipleChoiceField(
        widget=forms.CheckboxSelectMultiple,
        required=False
    )

    def __init__(self, *args, **kwargs):
        self.selected_files = kwargs.pop('selected_files', None)
        super().__init__(*args, **kwargs)

    class Meta:
        model = File
        fields = ('selected_files',)

class FolderListForm(forms.ModelForm):

    selected_folders = forms.MultipleChoiceField(
        widget=forms.CheckboxSelectMultiple,
        required=False
    )

    def __init__(self, *args, **kwargs):
        self.selected_folders = kwargs.pop('selected_folders', None)
        super().__init__(*args, **kwargs)

    class Meta:
        model = Folder
        fields = ('selected_folders',)
