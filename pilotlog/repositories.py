from django.db import models
from django.db import connection


class ImporterRepository:
    @staticmethod
    def truncate_importer_table() -> None:
        with connection.cursor() as cursor:
            cursor.execute('DELETE FROM pilotlog_importer')

    @staticmethod
    def all(model_link: models.Model):
        return model_link.objects.all()

    @staticmethod
    def bulk_create_importers(importers: list, model_link: models.Model) -> None:
        model_link.objects.bulk_create(importers)
