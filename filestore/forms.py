from django import forms
from .models import ClamAVSettings


# TODO: abstract common parts of these forms
class FileListForm(forms.Form):

    # handles operations on multiple Folder records from the file-list page
    selected_files = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple, required=False)

    def clean_selected_files(self):
        data = self.cleaned_data['selected_files']
        if not data:
            raise forms.ValidationError('Select at least one file to operate on')


class FolderListForm(forms.Form):

    # handles operations on multiple Folder records from the file-list page
    selected_folders = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple, required=False)

    def clean_selected_folders(self):
        data = self.cleaned_data['selected_folders']
        if not data:
            raise forms.ValidationError('Select at least one folder to operate on')


class ClamAVSettingsForm(forms.ModelForm):

    class Meta:
        model = ClamAVSettings
        fields = ['enabled', ]
