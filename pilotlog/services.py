import json
import time
import csv
from io import StringIO

from django.db import models
from django.apps import apps
from django.http import HttpResponse

from pilotlog.repositories import ImporterRepository


class BaseService:
    __slots__ = ['__model_name', '__app_name', '_model']

    def __init__(self, model_name: str, app_name: str):
        self.__model_name = model_name
        self.__app_name = app_name
        self._model = apps.get_model(self.__app_name, self.__model_name)


class ImporterService(BaseService):
    def create_importers_from_json(self, json_data: list) -> list:
        importers = []
        for item in json_data:
            importer = self._model(
                user_id=item.get('user_id'),
                table=item.get('table'),
                guid=item.get('guid'),
                meta=item.get('meta'),
                platform=item.get('platform'),
                _modified=item.get('_modified', int(time.time()))
            )
            importers.append(importer)
        return importers

    def save(self, importers):
        ImporterRepository.bulk_create_importers(importers, self._model)


class ExporterService(BaseService):
    def get_download_response(self):
        pseudo_buffer = StringIO()
        writer = csv.writer(pseudo_buffer)

        field_names = [field.name for field in self._model._meta.get_fields() if field.concrete]
        writer.writerow(field_names)

        queryset = self._model.objects.all()

        for obj in queryset:
            row = [getattr(obj, field) for field in field_names]
            writer.writerow(row)

        response = HttpResponse(pseudo_buffer.getvalue(), content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="data_export.csv"'

        return response
