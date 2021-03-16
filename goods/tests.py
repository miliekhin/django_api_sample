from unittest import mock
from django.test import TestCase
from .views import CategoriesByIdView
from django.test.client import RequestFactory


class TestCategory(TestCase):

    def test_category(self):
        mock_json = [{'id': 3, 'name': 'Category Name'}]

        with mock.patch('goods.views.CategoriesByIdView.get') as mock_get:
            mock_get.return_value.status_code = 200
            mock_get.return_value.json.return_value = mock_json
            rf = RequestFactory()
            request = rf.get('/v1/categories/1/')
            response = CategoriesByIdView.as_view()(request)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json(), mock_json)
