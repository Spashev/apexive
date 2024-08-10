import datetime

from django.db import models


class Importer(models.Model):
    user_id = models.PositiveIntegerField(null=True, blank=True)
    table = models.CharField(max_length=255, null=True, blank=True)
    guid = models.CharField(max_length=255, null=True, blank=True)
    meta = models.JSONField(null=True, blank=True)
    platform = models.CharField(max_length=255, null=True, blank=True)
    _modified = models.BigIntegerField(null=True, blank=True)

    def __str__(self):
        return f"{self.table} - {self.guid}"

    @property
    def modified(self):
        return datetime.datetime.fromtimestamp(self._modified)
