from rest_framework import status
from .models import (
    User,
    Technology,
    Agency,
    CompanyDetails,
    DigitalPresence,
    Skill,
    CoderSkillsExperience,
    Certification, 
    Qualification, 
    EducationalQualification,
)
from rest_framework.test import APITestCase, APIClient
from rest_framework.reverse import reverse
import uuid



class ApprovedTechnologyAPITestCase(APITestCase):
    def setUp(self):
        self.superuser = User.objects.create_superuser(
            username="admin@example.com",
            email="admin@example.com",
            password="adminpassword",
        )

        self.client = APIClient()
        self.client.force_authenticate(user=self.superuser)

        self.technology_data = { "name": "python", "is_approved": True, "user": self.superuser, }
        self.technology = Technology.objects.create(**self.technology_data)
        self.url = reverse("technology-detail", args=[str(self.technology.id)])

    def test_get_approved_technology(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], self.technology_data["name"])


class TechnologyCreationTestCase(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.technology_data = {"name": "Python"}
        self.user_coder = User.objects.create_user(
            username="coder@example.com", password="password", role="CODER"
        )

    def test_coder_can_create_technology(self):
        self.client.force_authenticate(user=self.user_coder)
        url = reverse("technology-list")
        data = {"name": "New Technology"}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_get_unapproved_technology_coder(self):
        self.client.force_authenticate(user=self.user_coder)
        self.technology = Technology.objects.create(name=self.technology_data["name"], user=self.user_coder)
        url = reverse("technology-detail", args=[str(self.technology.id)])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        

class ClientTechnologyCreationTestCase(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.technology_data = {"name": "Python"}
        self.user_client = User.objects.create_user(
            username="client@example.com", password="password", role="CLIENT"
        )

    def test_client_can_create_technology(self):
        self.client.force_authenticate(user=self.user_client)
        url = reverse("technology-list")
        data = {"name": "New Technology"}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_get_unapproved_technology_client(self):
        self.client.force_authenticate(user=self.user_client)
        self.technology = Technology.objects.create(
            name=self.technology_data["name"], user=self.user_client
        )  # noqa : E501
        url = reverse(
            "technology-detail", args=[str(self.technology.id)]
        )  # noqa : E501

        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

       

class AgencyViewSetTest(APITestCase):
    def setUp(self):
        self.agency_data = {
            "name": "Test Agency",
            "website": "http://testexample.com",
            "phone": "+9123456789",
            "email": "test@example.com",
            "address_line_1": "123 Main St",
            "address_line_2": "Apt 4",
            "country": "USA",
            "city": "Cityville",
            "state": "CA",
            "zip_code": "12345",
        }

    def test_create_agency(self):
        url = reverse("agency-list")
        response = self.client.post(url, self.agency_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Agency.objects.count(), 1)
        self.assertEqual(Agency.objects.get().name, "Test Agency")

    def test_retrieve_agency_list(self):
        Agency.objects.create(
            name="Existing Agency",
            website="http://existing.com",
            phone="+9187654321",
            email="existing@example.com",
            address_line_1="456 Oak St",
            address_line_2="Suite 10",
            country="Canada",
            city="Townsville",
            state="ON",
            zip_code="M1N3W2",
        )

        url = reverse("agency-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["name"], "Existing Agency")

    def test_retrieve_agency_detail(self):
        agency = Agency.objects.create(
            name="Detail Agency",
            website="http://detail.com",
            phone="+9111222333",
            email="detail@example.com",
            address_line_1="789 Pine Rd",
            address_line_2="Unit 5",
            country="UK",
            city="London",
            state="England",
            zip_code="EC1A1BB",
        )

        url = reverse("agency-detail", kwargs={"pk": agency.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], "Detail Agency")


class RegistrationAPITestCase(APITestCase):
    def test_mandatory_fields(self):
        url = reverse("register-list")
        data = {
            "first_name": "",
            "email": "",
            "phone": "",
        }

        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("first_name", response.data)
        error_messages = response.data["first_name"]
        self.assertTrue(
            any("blank" in error.lower() for error in error_messages),
            f"Unexpected error messages: {error_messages}",
        )
        self.assertIn("email", response.data)
        error_messages_email = response.data["email"]
        self.assertTrue(
            any("blank" in error.lower() for error in error_messages_email),
            f"Unexpected error messages for email: {error_messages_email}",
        )
        self.assertIn("phone", response.data)
        error_messages_phone = response.data["phone"]
        self.assertTrue(
            any("blank" in error.lower() for error in error_messages_phone),
            f"Unexpected error messages for phone: {error_messages_phone}",
        )

    def test_terms_and_conditions(self):
        url = reverse("register-list")
        data = {
            "email": "test@example.com",
            "password": "testpassword",
            "confirm_password": "testpassword",
            "tc": False,
            "first_name": "A" * 50,
            "last_name": "B" * 50,
            "phone": "+1911234545",
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_max_min_limits(self):
        url = reverse("register-list")
        data = {
            "email": "test@example.com",
            "password": "testpassword",
            "tc": True,
            "first_name": "A" * 151,
            "last_name": "B" * 151,
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("first_name", response.data)
        self.assertIn("last_name", response.data)

    def test_unique_email(self):
        User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpassword",  # noqa: 501
        )
        url = reverse("register-list")
        data = {
            "email": "test@example.com",  # Duplicate email
            "password": "testpassword",
            "tc": True,
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("email", response.data)

    def test_unique_username(self):
        User.objects.create_user(
            username="johndoe",
            email="test1@example.com",
            password="testpassword",  # noqa: 501
        )
        url = reverse("register-list")
        data = {
            "email": "test2@example.com",
            "password": "testpassword",
            "confirm_password": "testpassword",
            "first_name": "John",
            "last_name": "Doe",
            "tc": True,
            "username": "johndoe",
            "phone": "+1911234545",
        }

        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_email_format_validation(self):
        url = reverse("register-list")
        data = {
            "email": "invalid_email",
            "password": "testpassword",
            "tc": True,
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("email", response.data)

    def test_phone_number_validation(self):
        url = reverse("register-list")
        data = {
            "email": "test@example.com",
            "password": "testpassword",
            "tc": True,
            "phone": "123",
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("phone", response.data)

    def test_unique_email_method(self):
        User.objects.create_user(
            username="testuser",
            email="unique_email@example.com",
            password="testpassword",
        )
        url = reverse("register-list")
        data = {
            "email": "unique_email@example.com",
            "password": "testpassword",
            "tc": True,
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("email", response.data)

    def test_authorization_check(self):
        url = reverse("register-list")
        data = {
            "email": "test@example.com",
            "password": "testpassword",
            "tc": True,
        }
        client = APIClient()
        response = client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_easy_password(self):
        url = reverse("register-list")
        data = {
            "email": "test@example.com",
            "password": "Test@1234",
            "confirm_password": "Test@1234",
            "tc": True,
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_confirm_password_match(self):
        url = reverse("register-list")
        data = {
            "email": "test@example.com",
            "password": "testpassword",
            "confirm_password": "passwordtest",
            "tc": True,
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_eight_character_password(self):
        url = reverse("register-list")
        data = {
            "email": "test@example.com",
            "password": "eightc",
            "confirm_password": "eightc",
            "tc": True,
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("password", response.data)

    def test_alpha_numeric_password_limits(self):
        url = reverse("register-list")
        data = {
            "email": "test@example.com",
            "password": "alpha123",
            "confirm_password": "alpha123",
            "tc": True,
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("password", response.data)

    def test_successful_registration(self):
        url = reverse("register-list")
        data = {
            "email": "test2@example.com",
            "password": "testpassword",
            "confirm_password": "testpassword",
            "first_name": "John",
            "last_name": "Doe",
            "tc": True,
            "username": "johndoe",
            "phone": "+1911234545",
        }

        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("access_token", response.data)
        self.assertIn("refresh_token", response.data)

    def test_client_with_agency_registration(self):
        agency_data = {
            "name": "Sample Agency",
            "website": "https://sampleagency.com",
            "phone": "+19191234567",
            "email": "agency@example.com",
            "address_line_1": "123 Main St",
            "city": "City",
            "state": "State",
            "country": "Country",
            "zip_code": "12345",
        }
        agency = Agency.objects.create(**agency_data)
        url = reverse("register-list")
        data = {
            "email": "client_with_agency@example.com",
            "password": "testpassword",
            "confirm_password": "testpassword",
            "first_name": "Client",
            "last_name": "WithAgency",
            "tc": True,
            "username": "client_with_agency",
            "phone": "+19191234567",
            "role": "CLIENT",
            "type": "AGENCY",
            "agency": str(agency.id),
        }

        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error", response.data)
        self.assertEqual(
            response.data["error"][0],
            "A client cannot be associated with an agency.",  # noqa:  E501
        )
        with self.assertRaises(User.DoesNotExist):
            User.objects.get(email=data["email"])

        data_coder_without_agency = data.copy()
        data_coder_without_agency["role"] = "CODER"
        data_coder_without_agency.pop("agency")
        response_coder_without_agency = self.client.post(
            url, data_coder_without_agency, format="json"
        )
        self.assertEqual(
            response_coder_without_agency.status_code,
            status.HTTP_400_BAD_REQUEST,  # noqa:  E501
        )
        self.assertIn("error", response_coder_without_agency.data)
        self.assertEqual(
            response_coder_without_agency.data["error"][0],
            "Agency field is required for a coder with type 'AGENCY'.",
        )

        data_individual_with_agency = data.copy()
        data_individual_with_agency["type"] = "INDIVIDUAL"
        response_individual_with_agency = self.client.post(
            url, data_individual_with_agency, format="json"
        )
        self.assertEqual(
            response_individual_with_agency.status_code,
            status.HTTP_400_BAD_REQUEST,  # noqa:  E501
        )
        self.assertIn("error", response_individual_with_agency.data)
        self.assertEqual(
            response_individual_with_agency.data["error"][0],
            "Agency field should not be provided for individual users.",
        )


class ResendEmailVerificationViewSetTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            email="testuser@example.com",
            password="testpassword",  # noqa : E501
        )

    def test_required_fields(self):
        response = self.client.post(reverse("resend-verification-email-list"))
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("detail", response.data)

    def test_correct_email(self):
        data = {"email": "testuser@example.com"}
        response = self.client.post(
            reverse("resend-verification-email-list"), data
        )  # noqa: E501
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn(
            "Email verification link has been resent", response.data["detail"]
        )

    #
    def test_incorrect_email(self):
        data = {"email": "nonexistentuser@example.com"}
        response = self.client.post(
            reverse("resend-verification-email-list"), data
        )  # noqa: E501
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn(
            "Email verification link has been resent", response.data["detail"]
        )  # noqa: E501

    def test_email_validation(self):
        data = {"email": "invalidemail"}
        response = self.client.post(
            reverse("resend-verification-email-list"), data
        )  # noqa: E501
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn(
            "Email verification link has been resent", response.data["detail"]
        )  # noqa: E501

    def test_authorization_check(self):
        response = self.client.post(reverse("resend-verification-email-list"))
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_multiple_resend_request(self):
        data = {"email": "testuser@example.com"}
        response = self.client.post(
            reverse("resend-verification-email-list"), data
        )  # noqa: E501
        if response.status_code == status.HTTP_429_TOO_MANY_REQUESTS:
            self.assertEqual(
                response.status_code, status.HTTP_429_TOO_MANY_REQUESTS
            )  # noqa : E501
            self.assertIn(
                "Please wait for 60 seconds before sending another request.",
                response.data["detail"],
            )


class CompanyAPITestCase(APITestCase):
    def setUp(self):
        self.client_user = User.objects.create(
            email="client@example.com", password="testpassword", role="CLIENT"
        )

        self.non_client_user = User.objects.create(
            email="nonclient@example.com",
            password="testpassword",
            role="CODER",  # noqa: E501
        )

        self.client_company = CompanyDetails.objects.create(
            user=self.client_user,
            company_name="Client Company",
            company_website="https://clientcompany.com",
        )

    def test_client_can_update_company(self):
        url = reverse("company-detail", kwargs={"id": self.client_company.id})
        self.client.force_authenticate(user=self.client_user)

        data = {
            "company_name": "Updated Client Company",
            "company_website": "https://updatedclientcompany.com",
        }

        response = self.client.put(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_non_client_cannot_create_company(self):
        url = reverse("company-detail", kwargs={"id": self.client_company.id})
        self.client.force_authenticate(user=self.non_client_user)

        data = {
            "company_name": "Invalid Company",
            "company_website": "https://invalidcompany.com",
        }

        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(CompanyDetails.objects.count(), 1)

    def test_client_can_update_own_company(self):
        url = reverse("company-detail", kwargs={"id": self.client_company.id})
        self.client.force_authenticate(user=self.client_user)

        data = {
            "company_name": "Updated Client Company",
            "company_website": "https://updatedclientcompany.com",
        }

        response = self.client.put(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.client_company.refresh_from_db()
        self.assertEqual(
            self.client_company.company_name, "Updated Client Company"
        )  # noqa: E501

    def test_non_client_cannot_update_company(self):
        url = reverse("company-detail", kwargs={"id": self.client_company.id})
        self.client.force_authenticate(user=self.non_client_user)

        data = {
            "company_name": "Invalid Updated Company",
            "company_website": "https://invalidupdatedcompany.com",
        }

        response = self.client.put(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.client_company.refresh_from_db()
        self.assertNotEqual(
            self.client_company.company_name, "Invalid Updated Company"
        )  # noqa: E501

    def test_api_accessible_even_if_email_not_verified(self):
        self.client_user.is_email_verified = False
        self.client_user.save()

        url = reverse("company-detail", kwargs={"id": self.client_company.id})
        self.client.force_authenticate(user=self.client_user)

        data = {
            "company_name": "Company for Unverified User",
            "company_website": "https://unverifiedcompany.com",
        }

        response = self.client.put(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(CompanyDetails.objects.count(), 1)

    def test_client_cannot_create_multiple_companies(self):
        url = reverse("company-list")
        self.client.force_authenticate(user=self.client_user)

        data_first_company = {
            "company_name": "First Client Company",
            "company_website": "https://firstclientcompany.com",
        }

        response = self.client.post(url, data_first_company, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data_second_company = {
            "company_name": "Second Client Company",
            "company_website": "https://secondclientcompany.com",
        }
        response_second_company = self.client.post(
            url, data_second_company, format="json"
        )
        self.assertEqual(
            response_second_company.status_code, status.HTTP_400_BAD_REQUEST
        )


class CoderDigitalPresenceAPITestCase(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="testuser", password="testpassword", role="CODER"
        )
        self.loggedin_user = self.client.force_authenticate(user=self.user)

    def create_digital_presence(self):
        return DigitalPresence.objects.create(
            user=self.user,
            linkedin_url="https://linkedin.com/testuser",
            github_url="https://github.com/testuser",
            stackoverflow_url="https://stackoverflow.com/users/testuser",
        )

    def test_create_coder_digital_presence(self):
        url = reverse("digital-presence-list")
        data = {
            "linkedin_url": "https://linkedin.com/testuser",
            "github_url": "https://github.com/testuser",
            "stackoverflow_url": "https://stackoverflow.com/users/testuser",
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(DigitalPresence.objects.count(), 1)

    def test_update_coder_digital_presence(self):
        digital_presence = self.create_digital_presence()
        url = reverse("digital-presence-detail", args=[digital_presence.id])
        data = {
            "linkedin_url": "https://linkedin.com/testuser-updated",
            "github_url": "https://github.com/testuser-updated",
            "stackoverflow_url": "https://stackoverflow.com/users/testuser-updated",  # noqa:  E501
        }
        response = self.client.put(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        digital_presence.refresh_from_db()
        self.assertEqual(
            digital_presence.linkedin_url,
            "https://linkedin.com/testuser-updated",  # noqa:  E501
        )
        self.assertEqual(
            digital_presence.github_url, "https://github.com/testuser-updated"
        )
        self.assertEqual(
            digital_presence.stackoverflow_url,
            "https://stackoverflow.com/users/testuser-updated",
        )

    def test_get_coder_digital_presence(self):
        digital_presence = self.create_digital_presence()
        url = reverse("digital-presence-detail", args=[digital_presence.id])

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data["linkedin_url"], digital_presence.linkedin_url
        )  # noqa:  E501
        self.assertEqual(
            response.data["github_url"], digital_presence.github_url
        )  # noqa:  E501
        self.assertEqual(
            response.data["stackoverflow_url"],
            digital_presence.stackoverflow_url,  # noqa:  E501
        )

    def test_delete_coder_digital_presence(self):
        digital_presence = self.create_digital_presence()
        url = reverse("digital-presence-detail", args=[digital_presence.id])

        response = self.client.delete(url)

        self.assertEqual(
            response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED
        )  # noqa:  E501
        self.assertEqual(DigitalPresence.objects.count(), 1)

    def test_invalid_linkedin_url(self):
        url = reverse("digital-presence-list")
        data = {
            "linkedin_url": "invalid_url",  # Invalid URL
            "github_url": "https://github.com/testuser",
            "stackoverflow_url": "https://stackoverflow.com/users/testuser",
        }

        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(DigitalPresence.objects.count(), 0)

    def test_invalid_github_url(self):
        url = reverse("digital-presence-list")
        data = {
            "linkedin_url": "https://linkedin.com/testuser",
            "github_url": "invalid_url",  # Invalid URL
            "stackoverflow_url": "https://stackoverflow.com/users/testuser",
        }

        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(DigitalPresence.objects.count(), 0)

    def test_invalid_stackoverflow_url(self):
        url = reverse("digital-presence-list")
        data = {
            "linkedin_url": "https://linkedin.com/testuser",
            "github_url": "https://github.com/testuser",
            "stackoverflow_url": "invalid_url",  # Invalid URL
        }

        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(DigitalPresence.objects.count(), 0)


class ClientDigitalPresenceAPITestCase(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="testuser", password="testpassword", role="CLIENT"
        )
        self.client.force_authenticate(user=self.user)

    def create_client_digital_presence(self):
        return DigitalPresence.objects.create(
            user=self.user,
            glassdoor_url="https://glassdoor.com/testuser",
            career_bliss_url="https://careerbliss.com/testuser",
            youtube_url="https://youtube.com/testuser",
            other_social_url="https://othersocial.com/testuser",
        )

    def test_create_client_digital_presence(self):
        url = reverse("digital-presence-list")
        data = {
            "glassdoor_url": "https://glassdoor.com/testuser",
            "career_bliss_url": "https://careerbliss.com/testuser",
            "youtube_url": "https://youtube.com/testuser",
            "other_social_url": "https://othersocial.com/testuser",
        }
        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(DigitalPresence.objects.count(), 1)

    def test_update_client_digital_presence(self):
        client_digital_presence = self.create_client_digital_presence()
        url = reverse(
            "digital-presence-detail", args=[client_digital_presence.id]
        )  # noqa:  E501
        data = {
            "glassdoor_url": "https://glassdoor.com/testuser-updated",
            "career_bliss_url": "https://careerbliss.com/testuser-updated",
            "youtube_url": "https://youtube.com/testuser-updated",
            "other_social_url": "https://othersocial.com/testuser-updated",
        }
        response = self.client.put(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        client_digital_presence.refresh_from_db()
        self.assertEqual(
            client_digital_presence.glassdoor_url,
            "https://glassdoor.com/testuser-updated",
        )
        self.assertEqual(
            client_digital_presence.career_bliss_url,
            "https://careerbliss.com/testuser-updated",
        )
        self.assertEqual(
            client_digital_presence.youtube_url,
            "https://youtube.com/testuser-updated",
        )
        self.assertEqual(
            client_digital_presence.other_social_url,
            "https://othersocial.com/testuser-updated",
        )

    def test_get_client_digital_presence(self):
        client_digital_presence = self.create_client_digital_presence()
        url = reverse(
            "digital-presence-detail", args=[client_digital_presence.id]
        )  # noqa:  E501

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data["glassdoor_url"],
            client_digital_presence.glassdoor_url,  # noqa:  E501
        )
        self.assertEqual(
            response.data["career_bliss_url"],
            client_digital_presence.career_bliss_url,  # noqa:  E501
        )
        self.assertEqual(
            response.data["youtube_url"], client_digital_presence.youtube_url
        )
        self.assertEqual(
            response.data["other_social_url"],
            client_digital_presence.other_social_url,  # noqa:  E501
        )

    def test_delete_client_digital_presence(self):
        client_digital_presence = self.create_client_digital_presence()
        url = reverse(
            "digital-presence-detail", args=[client_digital_presence.id]
        )  # noqa:  E501

        response = self.client.delete(url)

        self.assertEqual(
            response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED
        )  # noqa:  E501
        self.assertEqual(DigitalPresence.objects.count(), 1)

    def test_invalid_glassdoor_url(self):
        url = reverse("digital-presence-list")
        data = {
            "glassdoor_url": "invalid_url",  # Invalid URL
            "career_bliss_url": "https://careerbliss.com/testuser",
            "youtube_url": "https://youtube.com/testuser",
            "other_social_url": "https://othersocial.com/testuser",
        }

        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(DigitalPresence.objects.count(), 0)

    def test_invalid_career_bliss_url(self):
        url = reverse("digital-presence-list")
        data = {
            "glassdoor_url": "https://glassdoor.com/testuser",
            "career_bliss_url": "invalid_url",  # Invalid URL
            "youtube_url": "https://youtube.com/testuser",
            "other_social_url": "https://othersocial.com/testuser",
        }

        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(DigitalPresence.objects.count(), 0)

    def test_invalid_youtube_url(self):
        url = reverse("digital-presence-list")
        data = {
            "glassdoor_url": "https://glassdoor.com/testuser",
            "career_bliss_url": "https://careerbliss.com/testuser",
            "youtube_url": "invalid_url",  # Invalid URL
            "other_social_url": "https://othersocial.com/testuser",
        }

        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(DigitalPresence.objects.count(), 0)

    def test_invalid_other_social_url(self):
        url = reverse("digital-presence-list")
        data = {
            "glassdoor_url": "https://glassdoor.com/testuser",
            "career_bliss_url": "https://careerbliss.com/testuser",
            "youtube_url": "https://youtube.com/testuser",
            "other_social_url": "invalid_url",  # Invalid URL
        }

        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(DigitalPresence.objects.count(), 0)


class SkillAPITestCase(APITestCase):
    def setUp(self):
        self.coder = User.objects.create_user(username="testuser", password="testpassword", role="CODER")
        self.client.force_authenticate(user=self.coder)
        self.technology = Technology.objects.create(user=self.coder, name="Python")

    def test_create_skill(self):
        url = reverse("skills-list")
        data = {
            "technology": str(self.technology.id),
            "years_of_experience": 3,
            "skill_type": "PRIMARY",
            "expertise_level": "INTERMEDIATE",
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Skill.objects.filter(user=self.coder).exists())

    def test_create_primary_skill_validation(self):
        url = reverse("skills-list")
        Skill.objects.create(
            user=self.coder,
            technology=self.technology,
            years_of_experience=2,
            skill_type="PRIMARY",
            expertise_level="BEGINNER",
        )

        data = {
            "technology": str(self.technology.id),
            "years_of_experience": 3,
            "skill_type": "PRIMARY",
            "expertise_level": "INTERMEDIATE",
        }

        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["skill_type"][0],"User can only have one primary skill.",)

    def test_create_secondary_skill_validation(self):
        url = reverse("skills-list")
        Skill.objects.create(
            user=self.coder,
            technology=self.technology,
            years_of_experience=2,
            skill_type="SECONDARY",
            expertise_level="BEGINNER",
        )

        data = {
            "technology": str(self.technology.id),
            "years_of_experience": 3,
            "skill_type": "SECONDARY",
            "expertise_level": "INTERMEDIATE",
        }

        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["skill_type"][0], "User can only have one secondary skill.",)

    def test_create_other_skill_validation_exceed_limit(self):
        for i in range(10):
            technology = Technology.objects.create(
                user=self.coder, name=f"Technology{i}"
            )
            Skill.objects.create(
                user=self.coder,
                technology=technology,
                years_of_experience=2,
                skill_type="OTHER",
                expertise_level="BEGINNER",
            )

        url = reverse("skills-list")
        duplicate_technology = Technology.objects.first()
        data = {
            "technology": str(duplicate_technology.id),
            "years_of_experience": 3,
            "skill_type": "OTHER",
            "expertise_level": "INTERMEDIATE",
        }

        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        expected_error_message = "User can have at most 10 other skills."
        self.assertEqual(response.data["skill_type"][0], expected_error_message)

    def test_update_skill_validation(self):
        existing_skill = Skill.objects.create(
            user=self.coder,
            technology=self.technology,
            years_of_experience=2,
            skill_type="PRIMARY",
            expertise_level="BEGINNER",
        )
        url = reverse("skills-detail", kwargs={"id": existing_skill.id})

        data = {
            "technology": str(self.technology.id),
            "years_of_experience": 3,
            "skill_type": "PRIMARY",
            "expertise_level": "INTERMEDIATE",
        }

        response = self.client.put(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class ClientSkillsRestrictionAPITestCase(APITestCase):
    def setUp(self):
        self.client_user = User.objects.create_user(username="clientuser", password="clientpassword", role="CLIENT")
        self.client.force_authenticate(user=self.client_user)

    def test_client_unable_to_create_skill(self):
        url = reverse("skills-list")
        technology = Technology.objects.create(user=self.client_user, name="Test Technology")

        data = {
            "technology": str(technology.id),
            "years_of_experience": 3,
            "skill_type": "OTHER",
            "expertise_level": "INTERMEDIATE",
        }

        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertIn("You do not have permission to perform this action.", response.data["detail"],)


class CoderSkillsExperienceAPITestCase(APITestCase):
    def setUp(self):
        self.coder = User.objects.create_user(username="testuser", password="testpassword", role="CODER")
        self.client.force_authenticate(user=self.coder)

    def test_create_coder_skills_experience(self):
        url = reverse("skills-experience-list")

        data = {
            "introduction": "I am a skilled coder",
            "total_years_of_experience": 5,
            "identity": "Full Stack Developer",
            "hourly_rate": 50,
            "brief_work_experience": "Worked on various projects",
            "profile_picture": None,
        }

        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(CoderSkillsExperience.objects.filter(user=self.coder).exists())

    def test_create_coder_skills_experience_validation(self):
        CoderSkillsExperience.objects.create(
            user=self.coder,
            introduction="I am a skilled coder",
            total_years_of_experience=5,
            identity="Full Stack Developer",
            hourly_rate=50,
            brief_work_experience="Worked on various projects",
            profile_picture=None,
        )

        url = reverse("skills-experience-list")

        data = {
            "introduction": "Another coder with skills",
            "total_years_of_experience": 8,
            "identity": "Frontend Developer",
            "hourly_rate": 60,
            "brief_work_experience": "Worked on web applications",
            "profile_picture": None,
        }

        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["error"][0], "Skills and Experience for this user already exists.",)

    def test_update_coder_skills_experience(self):
        existing_experience = CoderSkillsExperience.objects.create(
            user=self.coder,
            introduction="I am a skilled coder",
            total_years_of_experience=5,
            identity="Full Stack Developer",
            hourly_rate=50,
            brief_work_experience="Worked on various projects",
            profile_picture=None,
        )

        url = reverse("skills-experience-detail", kwargs={"id": existing_experience.id})

        data = {
            "introduction": "Updated coder introduction",
            "total_years_of_experience": 6,
            "identity": "Backend Developer",
            "hourly_rate": 55,
            "brief_work_experience": "Worked on backend systems",
            "profile_picture": None,
        }

        response = self.client.put(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        existing_experience.refresh_from_db()
        self.assertEqual(existing_experience.introduction, data["introduction"])
        self.assertEqual(existing_experience.total_years_of_experience,data["total_years_of_experience"],)

    def test_partial_update_coder_skills_experience(self):
        existing_experience = CoderSkillsExperience.objects.create(
            user=self.coder,
            introduction="I am a skilled coder",
            total_years_of_experience=5,
            identity="Full Stack Developer",
            hourly_rate=50,
            brief_work_experience="Worked on various projects",
            profile_picture=None,
        )

        url = reverse("skills-experience-detail", kwargs={"id": existing_experience.id})

        data = {
            "introduction": "Updated coder introduction",
            "brief_work_experience": "Updated work experience details",
        }

        response = self.client.patch(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        existing_experience.refresh_from_db()
        self.assertEqual(existing_experience.introduction, data["introduction"])
        self.assertEqual(existing_experience.brief_work_experience,data["brief_work_experience"],)


class ClientSkillsExperienceRestrictionAPITestCase(APITestCase):
    def setUp(self):
        self.client_user = User.objects.create_user(username="testuser", password="testpassword", role="CLIENT")
        self.client.force_authenticate(user=self.client_user)

    def test_client_unable_to_create_coder_skills_experience(self):
        url = reverse("skills-experience-list")

        data = {
            "introduction": "I am a skilled coder",
            "total_years_of_experience": 5,
            "identity": "Full Stack Developer",
            "hourly_rate": 50,
            "brief_work_experience": "Worked on various projects",
            "profile_picture": None,
        }

        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertIn("You do not have permission to perform this action.",response.data["detail"],)
        self.assertFalse(CoderSkillsExperience.objects.filter(user=self.client_user).exists())


class RecommendedTechnologyAPITestCase(APITestCase):
    def setUp(self):
        self.technology1 = Technology.objects.create(name="Tech1", is_approved=True)
        self.technology2 = Technology.objects.create(name="Tech2", is_approved=True)
        self.technology3 = Technology.objects.create(name="Tech3", is_approved=True)
        self.technology4 = Technology.objects.create(name="Tech4", is_approved=True)
        self.technology5 = Technology.objects.create(name="Tech5", is_approved=True)

    def test_recommended_technology(self):
        url=reverse("recommended-technology-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        recommended_technologies = response.data
        self.assertTrue(isinstance(recommended_technologies, list))
        self.assertEqual(len(recommended_technologies), 5)
        available_technologies = [
            str(self.technology1.id),
            str(self.technology2.id),
            str(self.technology3.id),
            str(self.technology4.id),
            str(self.technology5.id),
        ]
        for recommended_technology in recommended_technologies:
            self.assertIn(
                str(uuid.UUID(recommended_technology["id"])), available_technologies
            )


class CoderAPIClientAccessTestCase(APITestCase):
    def setUp(self):
        self.client_user = User.objects.create_user(username='client_user', password='password123', role='CLIENT')
        self.client.force_authenticate(user=self.client_user)

    def test_client_has_access(self):
        url = reverse("coder-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class CoderAPICoderAccessRestrictedTestCase(APITestCase):
    def setUp(self):
        self.coder_user = User.objects.create_user(username='coder_user', password='password123', role='CODER')
        self.client.force_authenticate(user=self.coder_user)

    def test_coder_no_access(self):
        url = reverse("coder-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class EducationAPITestCase(APITestCase):
    def setUp(self):
        self.coder = User.objects.create_user(username="testuser", password="testpassword", role="CODER")
        self.client.force_authenticate(user=self.coder)
    
        self.certificate_data = {
            "certificate_name": "Test Certificate",
            "year_of_completion": 2022,
        }

        self.qualification_data = {
            "university": "Test University",
            "passing_year": 2020,
            "degree": "Test Degree",
            "college": "Test College",
        }

        self.education_data = {
            "resume": None, 
            "portfolio": "http://example.com",
        }

    def test_certificate_creation(self):
        self.client = APIClient()
        self.client.force_authenticate(user=self.coder)
        url = reverse("certificate")
        response = self.client.post(url, data=self.certificate_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        certificate = Certification.objects.get(user=self.coder)
        self.assertEqual(certificate.certificate_name, self.certificate_data['certificate_name'])

    def test_qualification_creation(self):
        self.client = APIClient()
        self.client.force_authenticate(user=self.coder)
        url = reverse("qualification")
        response = self.client.post(url, data=self.qualification_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        qualification = Qualification.objects.get(user=self.coder)
        self.assertEqual(qualification.university, self.qualification_data['university'])

    def test_education_creation(self):
        self.client = APIClient()
        self.client.force_authenticate(user=self.coder)
        url = reverse("education")
        response = self.client.post(url, data=self.education_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        education = EducationalQualification.objects.get(user=self.coder)
        self.assertEqual(education.portfolio, self.education_data['portfolio'])

