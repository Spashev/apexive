import csv
from io import StringIO

from django.test import TestCase, Client
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from django.http import HttpResponse

from pilotlog.models import Importer
from pilotlog.forms import ImporterForm


class ImporterFormTests(TestCase):

    def test_valid_json_file(self):
        json_content = '{user_id: 1, table: "test", guid: "123", meta: {}, platform: "web", _modified: 1616317613}'
        file = SimpleUploadedFile('test.json', json_content.encode('utf-8'), content_type='application/json')
        form = ImporterForm(files={'file': file})
        self.assertTrue(form.is_valid())

    def test_invalid_file_extension(self):
        text_content = 'This is not a JSON file.'
        file = SimpleUploadedFile('test.txt', text_content.encode('utf-8'), content_type='text/plain')
        form = ImporterForm(files={'file': file})
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['file'], ['Only JSON files are allowed.'])

    def test_file_size_exceeds_limit(self):
        large_content = 'x' * (ImporterForm.MAX_FILE_SIZE_MB * 1024 * 1024 + 1)
        file = SimpleUploadedFile('large_file.json', large_content.encode('utf-8'), content_type='application/json')
        form = ImporterForm(files={'file': file})
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['file'], [f'File size exceeds the {ImporterForm.MAX_FILE_SIZE_MB} MB limit.'])

    def test_invalid_json_content(self):
        invalid_json_content = '{\"user_id\": 1, \"table\": "test", \"guid\": "123"}'
        file = SimpleUploadedFile('invalid.json', invalid_json_content.encode('utf-8'), content_type='application/json')
        form = ImporterForm(files={'file': file})
        self.assertTrue(form.is_valid())


class ExporterViewTests(TestCase):
    def setUp(self):
        Importer.objects.create(
            user_id=1,
            table="test_table",
            guid="123",
            meta={"key": "value"},
            platform="web",
            _modified=1616317613
        )

    def test_export_csv(self):
        client = Client()
        url = reverse('exporter')

        response = client.post(url)

        self.assertEqual(response.status_code, 200)

        self.assertEqual(response['Content-Type'], 'text/csv')

        self.assertEqual(response['Content-Disposition'], 'attachment; filename="data_export.csv"')

        content = response.content.decode('utf-8')
        pseudo_buffer = StringIO(content)
        reader = csv.reader(pseudo_buffer)

        headers = next(reader)
        self.assertIn('user_id', headers)
        self.assertIn('table', headers)
        self.assertIn('guid', headers)
        self.assertIn('meta', headers)
        self.assertIn('platform', headers)
        self.assertIn('_modified', headers)

        row = next(reader)
        self.assertEqual(row[1], '1')
        self.assertEqual(row[2], 'test_table')
        self.assertEqual(row[3], '123')
        self.assertEqual(row[5], 'web')
        self.assertEqual(row[6], '1616317613')

    def test_export_csv_error_handling(self):
        with self.settings(EXPORTER_SERVICE_ERROR=True):
            client = Client()
            url = reverse('exporter')
            response = client.post(url)
            self.assertEqual(response.status_code, 200)
