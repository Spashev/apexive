import json
import time

from django.db import models

from pilotlog.repositories import ImporterRepository


class ExtractorService:
    @staticmethod
    def process_json_file(file) -> list | None:
        try:
            file_data = file.read().decode('utf-8')
            unescaped_json = file_data.replace('\\"', '"')
            json_data = json.loads(unescaped_json)
            if isinstance(json_data, list):
                return json_data
            else:
                raise ValueError("JSON data should be a list of objects.")
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON file: {str(e)}")


class ImporterService:
    @staticmethod
    def create_importers_from_json(json_data: list, model_link: models.Model) -> list:
        importers = []
        for item in json_data:
            importer = model_link(
                user_id=item.get('user_id'),
                table=item.get('table'),
                guid=item.get('guid'),
                meta=item.get('meta'),
                platform=item.get('platform'),
                _modified=item.get('_modified', int(time.time()))
            )
            importers.append(importer)
        return importers

    @staticmethod
    def save(importers, model_link: models.Model):
        ImporterRepository.bulk_create_importers(importers, model_link)
