from django.urls import path

from pilotlog.views import ImporterView, ExporterView

urlpatterns = [
    path('', ImporterView.as_view(), name='importer'),
    path('export/', ExporterView.as_view(), name='exporter'),
]
