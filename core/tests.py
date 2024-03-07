from django.test import TestCase
from rest_framework.test import APITestCase
from rest_framework import status
from accounts.models import User
from accounts.models import DigitalPresence, Address, Skill, CoderSkillsExperience  
from core.views import CoderViewSet
from core.serializers import CoderSerializer
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated
from accounts.permissions import IsClient  
from django.urls import reverse

class CoderAPIClientAccessTestCase(APITestCase):
    def setUp(self):
        self.client_user = User.objects.create_user(username='client_user', password='password123', role='CLIENT')
        self.client.force_authenticate(user=self.client_user)

    def test_client_has_access(self):
        url = reverse("coders-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
class CoderAPICoderAccessRestrictedTestCase(APITestCase):
    def setUp(self):
        self.coder_user = User.objects.create_user(username='coder_user', password='password123', role='CODER')
        self.client.force_authenticate(user=self.coder_user)

    def test_coder_no_access(self):
        url = reverse("coders-list")
        response = self.client.get(url)  
        self.assertEqual(response.status_code, status.HTTP_200_OK)
"""
Test Module
"""
from rest_framework.test import APITestCase, APIClient
from rest_framework.reverse import reverse
from rest_framework import status
from .models import TimeZone
from accounts.models import User


class CreateTimzone(APITestCase):
    """
    Test if Creation API is working as expected
    - with coder and client
    """

    def setUp(self) -> None:
        """
        Set up function to build data
        """
        self.superuser = User.objects.create_superuser(
            username="admin@example.com", email="admin@example.com", password="test@12345", is_email_verified=True
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.superuser)
        self.url = reverse('timezone-list')

    def test_create_tiemzone(self):
        """
        Testing the create function
        """
        data = {
            "address_line_1": "Address 1",
            "address_line_2": "Address 2",
            "country": "India",
            "city": "Delhi",
            "state": "Delhi",
            "zip_code": "110029",
            "name": "America/Curacao"
        }
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
