from django import forms


class ImporterForm(forms.Form):
    file = forms.FileField()

    def clean_file(self):
        file = self.cleaned_data.get('file')
        if file:
            if not file.name.endswith('.json'):
                raise forms.ValidationError("Only JSON files are allowed.")
        return file
