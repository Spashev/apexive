from django import forms


class ImporterForm(forms.Form):
    file = forms.FileField()

    MAX_FILE_SIZE_MB = 10

    def clean_file(self):
        file = self.cleaned_data.get('file')
        if file:
            if not file.name.endswith('.json'):
                raise forms.ValidationError("Only JSON files are allowed.")
            if file.size > self.MAX_FILE_SIZE_MB * 1024 * 1024:
                raise forms.ValidationError(f"File size exceeds the {self.MAX_FILE_SIZE_MB} MB limit.")
        return file
