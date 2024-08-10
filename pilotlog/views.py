from django.views import View
from django.core.paginator import Paginator
from django.shortcuts import render, redirect

from pilotlog import forms
from pilotlog.models import Importer
from pilotlog.services import ImporterService, ExtractorService
from pilotlog.repositories import ImporterRepository


class ImporterView(View):
    def get(self, request, *args, **kwargs):
        page = request.GET.get('page', 1)
        per_page = 10

        form = forms.ImporterForm()
        data = ImporterRepository.all(Importer)
        paginator = Paginator(data, per_page)
        paginated_objects = paginator.get_page(page)
        context = {
            "form": form,
            "data": paginated_objects,
            "page_obj": paginated_objects,
        }

        return render(request, "pilotlog/importer.html", context)

    def post(self, request, *args, **kwargs):
        form = forms.ImporterForm(request.POST, request.FILES)
        if form.is_valid():
            uploaded_file = request.FILES['file']
            try:
                ImporterRepository.truncate_importer_table()

                json_data = ExtractorService.process_json_file(uploaded_file)
                importers = ImporterService.create_importers_from_json(json_data, Importer)
                ImporterService.save(importers, Importer)
                return redirect('importer')
            except ValueError as e:
                form.add_error('file', str(e))
            except Exception as e:
                form.add_error('file', f"An unexpected error occurred: {str(e)}")
        return render(request, "pilotlog/importer.html", {"form": form})


class ExporterView(View):
    def get(self, request, *args, **kwargs):
        form = forms.ImporterForm()
        return render(request, "pilotlog/exporter.html", {"form": form})

    def post(self, request, *args, **kwargs):
        print(args, kwargs)

        return render(request, "pilotlog/exporter.html")
