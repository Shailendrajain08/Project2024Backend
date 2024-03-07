import uuid
from decimal import Decimal
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
import pytz
from accounts.models import Technology, User
from core.utils import file_field_validators
from mysite.settings import HIRECODER_FEE
from django.core.validators import MinValueValidator
from mysite.settings import HIRECODER_FEE
import datetime

BUDGET_CHOICES = (
    ("FIXED", "Fixed"),
    ("HOURLY", "Hourly"),
)


JOB_STATUS_CHOICES = (
    ("OPEN", "Open"),
    ("CLOSED", "Closed"),
    ("ACTIVE", "Active"),
    ("COMPLETED", "Completed"),
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


DURATION = (
    ("SHORT_TERM", "Short term"),
    ("MEDIUM_TERM", "Medium"),
    ("LONG_TERM", "Long"),
)

SIZE_OF_PROJECT = (
    ("SMALL", "Small"),
    ("MEDIUM", "Medium"),
    ("LARGE", "Large"),
)

CODER_RESIDE = (
    ("USA_ONLY", "Usa only"),
    ("ANYWHERE_IN_THE_WORLD", "Anywhere in the world"),
)

JOB_INVITATION_CHOICES = (
    ("SENT", "Invitation Sent"),
    ("READ", "Read"),
    ("PROPOSAL_SUBMITTED", "Proposal Submitted"),
    ("INVITATION_REJECTED", "Rejected By Coder"),
)

MILESTONE_STATUS = (
    ('PROPOSED', 'Proposed'),
    ('PENDING', 'Pending'),
    ('ACTIVE', 'Active'),
    ('COMPLETE', 'Complete'))

RATING_CHOICES = (
    (1, "1"),
    (2, "2"),
    (3, "3"),
    (4, "4"),
    (5, "5"),
)

JOB_PROPOSAL_STATUS = (
    ('SENT', 'Sent'),
    ('ACCEPTED_BY_CLIENT','Accepted by Client'),
    ('REJECTED_BY_CLIENT', 'Rejected by Client'),
    ('ACCEPTED_BY_CODER', 'Accepted by Coder'),
    ('REJECTED_BY_CODER', 'Rejected by Coder')
)

JOB_PROPOSAL_TYPE = (
    ('HOURLY','Hourly'),
    ('FIXED', 'Fixed')
)

PERCENTAGE_VALIDATOR = [MinValueValidator(0), MaxValueValidator(100)]

TIMESHEET_STATUS = {
    ("PENDING", "Pending"),
    ("APPROVED", "Approved"),
    ("REJECTED", "Rejected")
 }

PAYMENT_STATUS = {
    ('PAY_NOW', "Pay Now"),
    ("COMPLETED", "Completed"),
    ("FAILED", "Failed")
}


class Expertise(models.Model):
    pk_id = models.BigAutoField(primary_key=True, editable=False)
    id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)    
    expertise = models.CharField(
        choices=EXPERTISE_LEVEL_CHOICES, max_length=30, default="BEGINNER", unique=True
    )

    def __str__(self):
        return str(self.expertise)
    


class TimeZone(models.Model):
    """
    TimeZone Model class to handle database schema and query.
    - Property corrosponds to column in core_timezone table
    """    
    pk_id = models.BigAutoField(primary_key=True, editable=False)
    id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    name = models.CharField(
        max_length=50,
        choices=[(tz, tz) for tz in pytz.all_timezones],
        default="UTC",
    )
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)    

    def __str__(self):
        return str(self.name)



class JobPost(models.Model):
    pk_id = models.BigAutoField(primary_key=True, editable=False)
    id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)  # noqa:  E501
    technologies = models.ManyToManyField(Technology, blank=False)
    project_size = models.CharField(choices=SIZE_OF_PROJECT, max_length=30)
    budget_type = models.CharField(choices=BUDGET_CHOICES, max_length=30)
    expertise = models.ManyToManyField(Expertise, max_length=30, blank=True)
    duration = models.CharField(choices=DURATION, max_length=30)
    timezone = models.ManyToManyField(TimeZone, max_length=30, blank=False)
    attachment_1 = models.FileField(
        upload_to="jobpost/attachments",
        blank=True,
        null=True,
        validators=file_field_validators(),
    )
    attachment_2 = models.FileField(
        upload_to="jobpost/attachments",
        blank=True,
        null=True,
        validators=file_field_validators(),
    )
    attachment_3 = models.FileField(
        upload_to="jobpost/attachments",
        blank=True,
        null=True,
        validators=file_field_validators(),
    )
    status = models.CharField(
        choices=JOB_STATUS_CHOICES, max_length=50, default="OPEN"
    )
    maximum_budget = models.PositiveIntegerField(null=True, blank=True)
    maximum_hourly_rate = models.PositiveIntegerField(null=True, blank=True)
    minimum_hourly_rate = models.PositiveIntegerField(null=True, blank=True)
    preferred_coder_residence = models.CharField(
        choices=CODER_RESIDE, max_length=30, default="USA_ONLY"
    )
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.title)
    

class JobInvitation(models.Model):
    pk_id = models.BigAutoField(primary_key=True, editable=False)
    id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    coder = models.ForeignKey(User, on_delete=models.CASCADE, related_name="coder")
    client = models.ForeignKey(User, on_delete=models.CASCADE, related_name="client")
    jobpost = models.ForeignKey(JobPost, on_delete=models.CASCADE)
    status = models.CharField(
        choices=JOB_INVITATION_CHOICES, max_length=50, default="INVITATION_SENT"
    )
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['coder', 'client', 'jobpost'], name='unique_job_invitation')
        ]


class JobPostV2(models.Model):
    pk_id = models.BigAutoField(primary_key=True, editable=False)
    id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    technologies = models.ManyToManyField(Technology, blank=False)
    project_size = models.CharField(choices=SIZE_OF_PROJECT, max_length=30)
    budget_type = models.CharField(choices=BUDGET_CHOICES, max_length=30)
    expertise_is_beginner = models.BooleanField(default=False)
    expertise_is_intermediate = models.BooleanField(default=False)
    expertise_is_expert = models.BooleanField(default=False)
    duration = models.CharField(choices=DURATION, max_length=30)
    timezone = models.ManyToManyField(TimeZone, max_length=30, blank=False)
    attachment_1 = models.FileField(blank=True, null=True, validators=file_field_validators())
    attachment_2 = models.FileField(blank=True, null=True, validators=file_field_validators())
    attachment_3 = models.FileField(blank=True, null=True, validators=file_field_validators())
    status = models.CharField(choices=JOB_STATUS_CHOICES, max_length=50, default="OPEN")
    maximum_budget = models.PositiveIntegerField(null=True, blank=True)
    maximum_hourly_rate = models.PositiveIntegerField(null=True, blank=True)
    minimum_hourly_rate = models.PositiveIntegerField(null=True, blank=True)
    preferred_coder_residence = models.CharField(choices=CODER_RESIDE, max_length=30)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.title)

class MilestoneV2(models.Model):
    pk_id = models.BigAutoField(primary_key=True, editable=False)
    id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    job_post = models.ForeignKey(JobPostV2, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    description = models.TextField()
    time = models.PositiveIntegerField()
    fund_released = models.DecimalField(max_digits=14, decimal_places=2)
    milestone_status = models.CharField(choices=MILESTONE_STATUS, default="PROPOSED")
    file = models.FileField(blank=True, null=True, validators=file_field_validators())
    completed_date = models.DateTimeField(blank=True, null=True)
    completed_description = models.TextField(blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f"<Milestone> {self.name}"
    
class JobProposalV2(models.Model):
    pk_id = models.BigAutoField(primary_key=True, editable=False)
    id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    job_post = models.ForeignKey(JobPostV2, on_delete=models.CASCADE)
    proposal_description = models.TextField(blank=True, null=True)
    proposal_type = models.CharField(choices=JOB_PROPOSAL_TYPE)
    hourly_rate = models.DecimalField(max_digits=14, decimal_places=2, blank=True, null=True,
                                      validators=[MinValueValidator(Decimal("1.00"))])
    availability_per_week = models.PositiveIntegerField(blank=True, null=True)
    attachment_1 = models.FileField(blank=True, null=True, validators=file_field_validators())
    attachment_2 = models.FileField(blank=True, null=True, validators=file_field_validators())
    attachment_3 = models.FileField(blank=True, null=True, validators=file_field_validators())
    coder_fee = models.DecimalField(max_digits=14, decimal_places=2, blank=True, null=True)
    platform_fee = models.DecimalField(max_digits=14, decimal_places=2, blank=True, null=True)
    platform_fee_percentage = models.DecimalField(max_digits=14, decimal_places=2, blank=True, null=True,
                                                  validators=PERCENTAGE_VALIDATOR)
    total_project_cost = models.DecimalField(max_digits=14, decimal_places=2, blank=True, null=True)
    is_submitted = models.BooleanField(default=False)
    estimate_time = models.CharField(blank=True, null=True)
    status = models.CharField(choices=JOB_PROPOSAL_STATUS, default="SENT")
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f"<JobProposal> {self.job_post} {self.user}"


class JobContract(models.Model):
    """
        Model class for Job Contract
    """
    pk_id = models.BigAutoField(primary_key=True, editable=False)
    id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    job_proposal = models.ForeignKey(JobProposalV2, on_delete=models.CASCADE, blank=False, null=False)
    coder_id = models.ForeignKey(User, on_delete=models.CASCADE, related_name="coder_c")
    client_id = models.ForeignKey(User, on_delete=models.CASCADE, related_name="client_c")
    name = models.CharField(max_length=100)
    start_date = models.DateField(auto_now_add=True)
    end_date = models.DateTimeField(null=True)
    is_active = models.BooleanField(default=True)
    rating = models.IntegerField(choices=RATING_CHOICES, null=True)
    feedback = models.TextField()
    total_amount_earned = models.FloatField(default=0.0)
    total_hours_worked = models.IntegerField(default=0)
    hourly_rate = models.FloatField(blank=True, null=True)
    hirecoder_fee = models.FloatField(default=HIRECODER_FEE)
    is_hourly_rate = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    
    def __str__(self) -> str:
        return f"<JobContract> {self.name}"

class Timesheet(models.Model):
    pk_id = models.BigAutoField(primary_key=True, editable=False)
    id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField(default=datetime.date.today)
    job_contract = models.ForeignKey(JobContract, on_delete=models.CASCADE)
    start_time = models.TimeField(blank=True, null=True)
    end_time = models.TimeField(blank=True, null=True)
    total_hours = models.FloatField(default = 0.0)
    amount = models.FloatField(default = 0.0)
    description = models.CharField(max_length=1000, null=True, blank=True)
    payment_status = models.CharField(choices = PAYMENT_STATUS, default = "PAY_NOW")
    timesheet_status = models.CharField(choices=TIMESHEET_STATUS, default='PENDING')
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str("Timesheet_" + self.job_contract.name + "_" +str(self.date) +
                   "_" + str(self.user.username) + "_" + str(self.created))
