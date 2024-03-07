from rest_framework.test import APITestCase, APIClient
from accounts.models import User
from rest_framework.reverse import reverse
from rest_framework import status


class AdminDashBoardAPITestCase(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user_admin = User.objects.create_user(username="admin", email="admin@admin.com", role="ADMIN")

    def test_GetTotalCountTest(self):
        self.client.force_authenticate(self.user_admin)
        url = reverse("dashboard-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)