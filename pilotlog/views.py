import csv
from io import StringIO
from abc import ABC, abstractmethod

from django.apps import apps
from django.views import View
from django.http import HttpResponse
from django.core.paginator import Paginator
from django.shortcuts import render, redirect

from pilotlog import forms
from pilotlog.models import Importer
from pilotlog.apps import PilotlogConfig
from pilotlog.services import ImporterService, ExporterService
from pilotlog.repositories import ImporterRepository

from helpers.parser import ParseJson
from helpers.logger import log_exception


class BaseView(View):
    @property
    @abstractmethod
    def service(self):
        pass


class ImporterView(BaseView):
    @property
    def service(self):
        return ImporterService(model_name=Importer.__name__, app_name=PilotlogConfig.name)

    def get(self, request, *args, **kwargs):
        page = request.GET.get('page', 1)
        per_page = 10
        form = forms.ImporterForm()
        data = self.service.all()
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
                json_data = ParseJson.run(file=uploaded_file)
                importers = self.service.create_importers_from_json(json_data=json_data)
                self.service.save(importers=importers)
                return redirect('importer')
            except ValueError as e:
                form.add_error('file', str(e))
            except Exception as e:
                message = f"An unexpected error occurred: {str(e)}"
                log_exception(error=message)
                form.add_error('file', message)
        return render(request, "pilotlog/importer.html", {"form": form})


class ExporterView(BaseView):
    @property
    def service(self):
        return ExporterService(model_name=Importer.__name__, app_name=PilotlogConfig.name)

    def get(self, request, *args, **kwargs):
        return render(request, "pilotlog/exporter.html")

    def post(self, request, *args, **kwargs):
        try:
            return self.service.get_download_response()
        except Exception as e:
            message = f"An unexpected error occurred: {str(e)}"
            log_exception(error=message)
        return render(request, "pilotlog/exporter.html", context={"message": message})
