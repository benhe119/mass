from django import forms


class FileListForm(forms.Form):

    selected_files = forms.MultipleChoiceField(
        widget=forms.CheckboxSelectMultiple,
        required=False
    )

    def clean_selected_files(self):
        data = self.cleaned_data['selected_files']
        if not data:
            raise forms.ValidationError('Select at least one file to operate on')


class FolderListForm(forms.Form):

    selected_folders = forms.MultipleChoiceField(
        widget=forms.CheckboxSelectMultiple,
        required=False
    )

    def clean_selected_folders(self):
        data = self.cleaned_data['selected_folders']
        if not data:
            raise forms.ValidationError('Select at least one folder to operate on')
