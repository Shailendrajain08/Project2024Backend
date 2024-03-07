import uuid
from django.core.validators import RegexValidator, MinValueValidator, MaxValueValidator, MaxLengthValidator
from django.db import models
from django.contrib.auth.models import AbstractUser
from datetime import datetime

USER_ROLE_CHOICES = (
    ("CLIENT", "Client"),
    ("CODER", "Coder"),
    ("COWORKER", "Coworker"),
    ("SUCCESS-MANAGER", "Success-Manager"),
    ("SUPER-ADMIN", "Super-Admin"),
    ("SUB-ADMIN", "Sub-Admin"),
)

USER_TYPE_CHOICES = (
    ("INDIVIDUAL", "Individual"),
    ("AGENCY", "Agency"),
)

PROFILE_CHOICES = (
    ("CLIENT", "Client"),
    ("CODER", "Coder"),
)

BUDGET_CHOICES = (
    ("FIXED", "Fixed"),
    ("HOURLY", "Hourly"),
)

JOB_STATUS_CHOICES = (
    ("ACTIVE", "Active"),
    ("PROPOSALS-RECEIVED", "Proposals-received"),
    ("OFFERED", "Offered"),
    ("COMPLETED", "Completed"),
    ("Expired", "Expired"),
)

PAYMENT_TYPE = (
    ("MILESTONE-PAYMENT", "Milestone-payment"),
    ("TIMESHEET-PAYMENT", "Timesheet-payment"),
)

SKILL_CHOICES = (
    ("PRIMARY", "Primary"),
    ("SECONDARY", "Secondary"),
    ("OTHER", "Other"),
)

EXPERTISE_LEVEL_CHOICES = (
    ("BEGINNER", "Beginner"),
    ("INTERMEDIATE", "Intermediate"),
    ("EXPERT", "Expert"),
)


class Agency(models.Model):
    id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False, unique=True
    )
    name = models.CharField(max_length=255)
    website = models.URLField(blank=True, null=True)
    phone_regex = RegexValidator(
        regex=r"^\+?1?\d{10,14}$",
        message="Enter Phone Number in the format +91. Upto 15 digits allowed",
    )
    phone = models.CharField(
        validators=[phone_regex], max_length=15, blank=True, null=True
    )
    email = models.EmailField(
        max_length=255, unique=False, db_index=True, blank=True, null=True
    )
    address_line_1 = models.CharField(max_length=200, blank=True, null=True)
    address_line_2 = models.CharField(max_length=200, blank=True, null=True)
    country = models.CharField(max_length=100, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    state = models.CharField(max_length=100, blank=True, null=True)
    zip_code = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        validators=[
            RegexValidator(
                r"^[a-zA-Z0-9-]{1,10}$",
                message="Enter a valid alphanumeric ZIP code.",  # noqa: E501
            )
        ],
    )
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.name)


class User(AbstractUser):
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    email = models.EmailField(max_length=255, unique=True, db_index=True)
    username = models.CharField(
        max_length=150, blank=True, null=True, unique=True, db_index=True
    )
    phone_regex = RegexValidator(
        regex=r"^\+?1?\d{10,14}$",
        message="Enter Phone Number in the format +1. Upto 15 digits allowed",
    )
    phone = models.CharField(
        validators=[phone_regex], max_length=15, blank=True, null=True
    )
    tc = models.BooleanField(default=False)
    role = models.CharField(
        choices=USER_ROLE_CHOICES, max_length=30, default="CLIENT"
    )  # noqa:  E501
    type = models.CharField(
        choices=USER_TYPE_CHOICES, max_length=30, default="INDIVIDUAL"
    )
    agency = models.OneToOneField(
        Agency, on_delete=models.CASCADE, blank=True, null=True
    )
    is_email_verified = models.BooleanField(default=False)
    is_root_user = models.BooleanField(default=True)
    is_profile_complete = models.BooleanField(default=False)
    profile_completeness_percentage = models.DecimalField(
        max_digits=5, decimal_places=2, default=0.0
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username", "password"]

    def __str__(self):
        return str(self.email)


class Technology(models.Model):
    pk_id = models.BigAutoField(primary_key=True, editable=False)
    id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(
        max_length=255,
        unique=True,
    )
    is_approved = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.name)

    def save(self, *args, **kwargs):
        self.name = self.name.lower()
        super().save(*args, **kwargs)


class Address(models.Model):
    pk_id = models.BigAutoField(primary_key=True, editable=False)
    id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    address_line_1 = models.CharField(max_length=200, blank=True, null=True)
    address_line_2 = models.CharField(max_length=200, blank=True, null=True)
    country = models.CharField(max_length=100, null=True, blank=True)
    city = models.CharField(max_length=100, null=True, blank=True)
    state = models.CharField(max_length=100, null=True, blank=True)
    zip_code = models.CharField(
        max_length=10,
        validators=[
            RegexValidator(
                r"^[a-zA-Z0-9\- ]{1,10}$",
                message="Enter a valid zip code.",
            )
        ],
        blank=True,
        null=True,
    )
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.address_line_1}, {self.address_line_2}, {self.city}, {self.state}, {self.zip_code}, {self.country}"  # noqa: E501

    class Meta:
        verbose_name = "Address"
        verbose_name_plural = "Addresses"


class CompanyDetails(models.Model):
    pk_id = models.BigAutoField(primary_key=True, editable=False)
    id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    company_name = models.CharField(max_length=255, blank=True, null=True)
    company_website = models.URLField(blank=True, null=True)
    linkedin_url = models.URLField(blank=True, null=True)
    logo = models.ImageField(upload_to="company_logos/", blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.company_name)

    class Meta:
        verbose_name = "CompanyDetails"
        verbose_name_plural = "CompanyDetails"


class Skill(models.Model):
    pk_id = models.BigAutoField(primary_key=True, editable=False)
    id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='skills_of_user')
    technology = models.ForeignKey(Technology, on_delete=models.CASCADE)
    years_of_experience = models.PositiveIntegerField(validators=[MinValueValidator(0), MaxValueValidator(50)])
    skill_type = models.CharField(choices=SKILL_CHOICES, max_length=100, default="PRIMARY")
    expertise_level = models.CharField(choices=EXPERTISE_LEVEL_CHOICES, max_length=100, default="BEGINNER")
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.technology.name)


class CoderSkillsExperience(models.Model):
    pk_id = models.BigAutoField(primary_key=True, editable=False)
    id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    introduction = models.TextField(blank=True, null=True)
    total_years_of_experience = models.PositiveIntegerField(validators=[MinValueValidator(0), MaxValueValidator(50)])
    identity = models.CharField(max_length=100,)
    hourly_rate = models.PositiveIntegerField(validators=[MinValueValidator(5), MaxValueValidator(999)])
    brief_work_experience = models.TextField(validators=[MaxLengthValidator(1000)])  # noqa : E501
    profile_picture = models.ImageField(upload_to="profile_pictures/", blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.identity)


class DigitalPresence(models.Model):
    pk_id = models.BigAutoField(primary_key=True, editable=False)
    id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    linkedin_url = models.URLField(max_length=200, blank=True, null=True)
    github_url = models.URLField(max_length=200, blank=True, null=True)
    stackoverflow_url = models.URLField(max_length=200, blank=True, null=True)
    glassdoor_url = models.URLField(max_length=100, blank=True, null=True)
    career_bliss_url = models.URLField(max_length=100, blank=True, null=True)
    youtube_url = models.URLField(max_length=200, blank=True, null=True)
    other_social_url = models.URLField(max_length=200, blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.id)


class Certification(models.Model):
    """
    Model representing a user's certificates.
    """
    pk_id = models.BigAutoField(primary_key=True, editable=False)
    id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    certificate_name = models.CharField(max_length=100)
    year_of_completion = models.PositiveIntegerField(
        validators=[MinValueValidator(1960), MaxValueValidator(datetime.now().year)])
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.certificate_name)
    
   
class Degree(models.Model):
    """
    Model representing a user's qualifications.
    """
    pk_id = models.BigAutoField(primary_key=True, editable=False)
    id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    university = models.CharField(max_length=100)
    passing_year = models.PositiveIntegerField(
        validators=[MinValueValidator(1960), MaxValueValidator(datetime.now().year),])
    degree = models.CharField(max_length=100,)
    college = models.CharField(max_length=100,)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.degree)
    
    
class EducationalQualification(models.Model):
    """
    Model representing a user's education details.
    """
    pk_id = models.BigAutoField(primary_key=True, editable=False)
    id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    resume = models.FileField(upload_to="resume/", blank=True, null=True)
    portfolio = models.URLField(blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.portfolio)
