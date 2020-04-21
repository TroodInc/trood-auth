from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase, APIClient


class ProbeTestCase(APITestCase):
    def setUp(self):
        self.client = APIClient()

    def test_probe(self):
        url = reverse('api:probe-list')
        response = self.client.get(url)
        assert response.status_code == status.HTTP_200_OK
        for key in ('status', 'uptime', 'version'):
            assert key in response.data, response.json()
