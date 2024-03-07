# Create your tests here.
from rest_framework import status
from accounts.models import (
    User,
    Technology,
    Agency,
    CompanyDetails,
    DigitalPresence,
    Skill,
    CoderSkillsExperience,
)
from core.models import (
    JobPost,
    Expertise,
    EXPERTISE_LEVEL_CHOICES,
    TimeZone,
)
from rest_framework.test import APITestCase, APIClient
from rest_framework.reverse import reverse
import uuid
import pytz
from django.utils import timezone


class RecommendedJobsTest(APITestCase):
    def setUp(self):
        self.superuser = User.objects.create_superuser(
            username="admin@example.com",
            email="admin@example.com",
            password="adminpassword",
        )
        self.user_coder = User.objects.create_user(
            username='coder', email="coder@example.com", password="password", role="CODER", is_email_verified=True
        )   
        self.user_client = User.objects.create_user(
            username='client', email="client@example.com", password="password", role="CLIENT", is_email_verified=True
        )             

        self.client = APIClient()
        # self.client.force_authenticate(user=self.superuser)
        self.client.force_authenticate(user=self.user_client)

        self.technology_data = [
                { "name": "python", "is_approved": True, "user": self.superuser, },
                { "name": "java", "is_approved": True, "user": self.superuser, },
                { "name": "ruby", "is_approved": True, "user": self.superuser, },
            ]
        technology_objs = []
        for tech in self.technology_data:
            obj = Technology.objects.create(**tech)
            technology_objs.append(obj)
        expertise_objs = []
        for i in EXPERTISE_LEVEL_CHOICES:
            obj = Expertise.objects.create(expertise=i[0])
            expertise_objs.append(obj)
        timezone_objs = []
        for i in pytz.all_timezones[:5]:
            obj = TimeZone.objects.create(name=i)
            timezone_objs.append(obj)

        job_post_url = reverse("job-posts-list")

        self.job_names = []
        self.job_ids = []
        for i in range(6):
            job_name = f"job test {timezone.now().isoformat()}"
            self.job_names.append(job_name)
            data = {
                "title": job_name,
                "description": job_name,
                "technologies": [
                    str(technology_objs[0].id),
                    str(technology_objs[0].id),
                ],
                "project_size": "SMALL",
                "budget_type": "FIXED",
                "expertise": [
                    expertise_objs[0].id,
                    expertise_objs[1].id
                ],
                "duration": "SHORT_TERM",
                "timezone": [
                    str(timezone_objs[0].id),
                    str(timezone_objs[0].id),
                ],
                "attachment_1": None,
                "attachment_2": None,
                "attachment_3": None,
                "status": "ACTIVE",
                "maximum_budget": 2,
                "maximum_hourly_rate": 0,
                "minimum_hourly_rate": 0,
                "preferred_coder_residence": "USA_ONLY"
            }
            response = self.client.post(job_post_url, data, format="json")
            job_id = response.data.get('id')
            self.job_ids.append(job_id)

    def test_recommended_jobs(self):
        self.client.force_authenticate(user=self.user_coder)
        recommended_jobs_url = reverse("recommended-jobs-list")
        response = self.client.get(recommended_jobs_url)
        response_json = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(len(response_json['results'])==5)
        print('Hii::', response_json)
        for i in response_json['results']: 
            self.assertIn(i["id"], self.job_ids)
            self.assertIn(i["title"], self.job_names)
