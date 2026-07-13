# resources/tests.py
from django.test import TestCase
from rest_framework.test import APIClient
from.models import Resource

class ResourceTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.resource = Resource.objects.create(
            title='Test Resource',
            description='This is a test resource',
            url='https://example.com',
            type='book',
            author='Test Author'
        )

    def test_resource_list(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)

    def test_resource_detail(self):
        response = self.client.get(f'/{self.resource.id}/')
        self.assertEqual(response.status_code, 200)