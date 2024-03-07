"""
Serializers for Core Application
"""
from datetime import datetime
from collections import OrderedDict
import pytz
import uuid
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from accounts.models import Technology, User
from core.models import (
    Expertise,
    JobPost,
    JobProposalV2,
    MilestoneV2,
    TimeZone,
    JobInvitation, 
    JobPostV2,
    CODER_RESIDE,
    JobContract,
    Timesheet)

from accounts.serializers import (
    UserSerializer,
)


class ExpertiseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Expertise
        fields = (
            "id",
            "expertise",
        )


class TimeZoneSerializer(serializers.ModelSerializer):
    """
    TimeZoneSerializer class 
    - Model Serailizer (for Timezone Model)
    - Validation and formating for timezone name
    """

    class Meta:
        model = TimeZone
        fields = ["id", "name", "created", "updated"]
        read_only_fields = ["created", "updated"]

    def validate_name(self, value):
        """
        Checking if timzone available in database
        - params value (name of timezone)
        """
        if TimeZone.objects.filter(name=value).exists():
            raise serializers.ValidationError("Timezone with this name already exists.")
        return value

    def to_representation(self, instance):
        """
        Formating the name of timzone to match the requirement
        - GMT - 00:00 TImezoneName
        """
        represent = super(TimeZoneSerializer, self).to_representation(instance)
        time_info = pytz.timezone(instance.name).localize(datetime.now()).strftime('%z')
        represent["name"] = f"GMT{time_info[:-2]}:{time_info[3:]} {instance.name}"
        return represent


class JobPostSerializer(serializers.ModelSerializer):
    user = serializers.SlugRelatedField(slug_field="username", read_only=True)

    class Meta:
        model = JobPost
        fields = [
            "id",
            "user",
            "title",
            "description",
            "technologies",
            "project_size",
            "budget_type",
            "expertise",
            "duration",
            "timezone",
            "attachment_1",
            "attachment_2",
            "attachment_3",
            "status",
            "maximum_budget",
            "maximum_hourly_rate",
            "minimum_hourly_rate",
            "preferred_coder_residence",
            "created",
            "updated",
        ]
        read_only_fields = ["created", "updated"]

    @staticmethod
    def is_valid_uuid(uuid_str):
        try:
            uuid.UUID(str(uuid_str))
            return True
        except ValueError:
            return False

    def to_internal_value(self, data):
        technology_ids = data.get("technologies")
        errors = OrderedDict()

        try:
            if isinstance(technology_ids, list):
                for i in technology_ids:
                    if not self.is_valid_uuid(i):
                        raise ValidationError("technologies must be list of valid uuids")  # noqa: E501
                data["technologies"] = list(
                    Technology.objects.filter(id__in=technology_ids).values_list(
                        "pk_id", flat=True
                    )
                )
        except ValidationError as exc:
            errors['technologies'] = exc.detail
        try:
            timezone_ids = data.get("timezone")
            if isinstance(timezone_ids, list):
                for i in timezone_ids:
                    if not self.is_valid_uuid(i):
                        raise ValidationError("timezone_ids must be list of valid uuids")  # noqa: E501
                data["timezone"] = list(
                    TimeZone.objects.filter(id__in=timezone_ids).values_list(
                        "pk_id", flat=True
                    )
                )
        except ValidationError as exc:
            errors['timezone'] = exc.detail
        try:
            expertise_ids = data.get("expertise")
            if isinstance(expertise_ids, list):
                for i in expertise_ids:
                    if not self.is_valid_uuid(i):
                        raise ValidationError("expertise_ids must be list of valid uuids")  # noqa: E501
                data["expertise"] = list(
                    Expertise.objects.filter(id__in=expertise_ids).values_list(
                        "pk_id", flat=True
                    )
                )
        except ValidationError as exc:
            errors['expertise'] = exc.detail

        if errors:
            raise ValidationError(errors)
        data = super().to_internal_value(data)
        return data

    def validate(self, attrs):
        request_method = self.context['request'].method
        if request_method == 'POST':
            budget_type = self.initial_data.get("budget_type")

            if budget_type == "HOURLY":
                minimum_hourly_rate = attrs.get("minimum_hourly_rate")
                maximum_hourly_rate = attrs.get("maximum_hourly_rate")
                if minimum_hourly_rate is None or maximum_hourly_rate is None:
                    raise serializers.ValidationError(
                        "If budget type is hourly, then must input min/max hourly rate."
                    )

                if int(maximum_hourly_rate) <= int(minimum_hourly_rate):
                    raise serializers.ValidationError(
                        "Maximum Hourly Rate should be greater than Minimum hourly rate."
                    )
            elif budget_type == 'FIXED':
                if attrs.get("minimum_hourly_rate") or attrs.get("maximum_hourly_rate"):
                    raise serializers.ValidationError(
                        "If budget type is fixed, then you can not input min/max hourly rate."
                    )

            attrs['status'] = 'OPEN'
        if request_method == 'PATCH':
            if not (len(attrs) == 1 and 'status' in attrs):
                raise ValidationError('Can update status only.')
        return super().validate(attrs)

    def validate_maximum_budget(self, value):
        budget_type = self.initial_data.get("budget_type")

        if budget_type == "FIXED":
            if value is None or value <= 0:
                raise serializers.ValidationError(
                    "Maximum budget should be greater than 0."
                )
        elif budget_type == "HOURLY":
            value = 0

        return value

    def validate_timezone(self, value):
        if not len(value):
            raise ValidationError('Atleast one timezone is needed.')
        return value

    def to_representation(self, instance):
        representation = super().to_representation(instance)

        technology_data = instance.technologies.all().values("id", "name", "is_approved")
        representation["technologies"] = list(technology_data)

        timezone_data = instance.timezone.values_list("id", flat=True)
        formatted_timezones = [
            f"GMT{pytz.timezone(TimeZone.objects.get(id=timezone_id).name).localize(datetime.now()).strftime('%z')[:-2]}:00 {TimeZone.objects.get(id=timezone_id).name}"
            for timezone_id in timezone_data
        ]

        representation["timezone"] = formatted_timezones

        expertise_data = instance.expertise.values_list("expertise", flat=True)
        representation["expertise"] = expertise_data

        return representation


class JobInvitationSerializer(serializers.ModelSerializer):
    coder = serializers.SlugRelatedField(slug_field="username", write_only=True, queryset = User.objects.filter(role = "CODER"))
    client = UserSerializer(read_only=True)
    jobpost = serializers.SlugRelatedField(slug_field="id", write_only=True, queryset = JobPost.objects.filter(status__in = ('OPEN', 'ACTIVE')))
    coder_user = UserSerializer(source="coder", read_only=True)
    jobpost_details = JobPostSerializer(source="jobpost", read_only=True)
    
    class Meta:
        model = JobInvitation
        fields = [
            "id",
            "coder",
            "coder_user",
            "client",
            "jobpost",
            "jobpost_details",
            "status",
            "created",
            "updated"
        ]
        read_only_fields = ["created", "updated", "status"]


class JobInvitationPatchSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobInvitation
        fields = [
            "status"
        ]


class TechnologySlugSerializer(serializers.SlugRelatedField):
    def get_queryset(self):
        return Technology.objects.all()


class TimezoneSlugSerializer(serializers.SlugRelatedField):
    def get_queryset(self):
        return TimeZone.objects.all()


class JobPostV2Serializer(serializers.ModelSerializer):
    user = serializers.SlugRelatedField(slug_field="username", read_only=True)
    technologies = TechnologySlugSerializer(many=True, slug_field="name", allow_empty=False, allow_null=False)
    timezone = TimezoneSlugSerializer(many=True, slug_field="name", allow_empty=False, allow_null=False)

    class Meta:
        model = JobPostV2
        fields = ["id", "user", "title", "description", "technologies", "project_size", "budget_type",
                  "expertise_is_beginner", "expertise_is_intermediate", "expertise_is_expert", "duration", "timezone",
                  "attachment_1", "attachment_2", "attachment_3", "status", "maximum_budget", "maximum_hourly_rate",
                  "minimum_hourly_rate", "preferred_coder_residence", "created", "updated"]
        read_only_fields = ["status", "created", "updated"]

    def validate(self, attrs):
        budget_type = attrs.get("budget_type", None)
        maximum_hourly_rate = attrs.get("maximum_hourly_rate", None)
        minimum_hourly_rate = attrs.get("minimum_hourly_rate", None)
        maximum_budget = attrs.get("maximum_budget", None)

        if budget_type == "HOURLY" and maximum_hourly_rate is None:
            raise ValidationError(
                {"maximum_hourly_rate": "Maximum hourly rate cannot be None when budget type is hourly."})

        if budget_type == "HOURLY" and minimum_hourly_rate is None:
            raise ValidationError(
                {"minimum_hourly_rate": "Minimum hourly rate cannot be None when budget type is hourly."})

        if budget_type == "HOURLY" and maximum_hourly_rate < minimum_hourly_rate:
            raise ValidationError(
                {"maximum_hourly_rate": "Maximum hourly rate cannot be less than Minimum hourly rate.",
                 "minimum_hourly_rate": "Maximum hourly rate cannot be less than Minimum hourly rate."})

        if budget_type == "FIXED" and maximum_budget is None:
            raise ValidationError({"maximum_budget": "Maximum budget cannot be None when budget type is fixed."})

        return attrs

    def create(self, validated_data):
        budget_type = validated_data.get('budget_type', None)
        if budget_type is not None and budget_type == "FIXED":
            validated_data["maximum_hourly_rate"] = None
            validated_data["minimum_hourly_rate"] = None
        elif budget_type is not None and budget_type == "HOURLY":
            validated_data["maximum_budget"] = None
        return super().create(validated_data)


class JobPostV2UpdateSerializer(JobPostV2Serializer):
    technologies = TechnologySlugSerializer(many=True, slug_field="name", read_only=True)
    timezone = TimezoneSlugSerializer(many=True, slug_field="name", read_only=True)

    class Meta(JobPostV2Serializer.Meta):
        read_only_fields = ["id", "user", "title", "description", "technologies", "project_size", "budget_type",
                            "expertise_is_beginner", "expertise_is_intermediate", "expertise_is_expert", "duration",
                            "timezone", "attachment_1", "attachment_2", "attachment_3", "maximum_budget",
                            "maximum_hourly_rate", "minimum_hourly_rate", "preferred_coder_residence", "created",
                            "updated"]

class MilestoneV2Serializer(serializers.ModelSerializer):
    user = serializers.SlugRelatedField(slug_field="username", read_only=True)
    job_post = serializers.SlugRelatedField(slug_field="id", queryset=JobPostV2.objects.all())

    class Meta:
        model = MilestoneV2
        fields = ["id", "user", "job_post", "name", "description", "time", "fund_released", "milestone_status",
                  "file", "completed_date", "completed_description", "created", "updated"]
        read_only_fields = ["milestone_status", "file", "completed_date", "completed_description", "created", "updated"]

    def validate_job_post(self, job_post):
        if job_post and job_post.budget_type == "HOURLY":
            raise ValidationError("Milestone cannot be added for Hourly Job Type.")
        return job_post


class MilestoneV2UpdateClientSerializer(serializers.ModelSerializer):
    MILESTONE_STATUS = (
        ('COMPLETE', 'Complete'),
    )
    user = serializers.SlugRelatedField(slug_field="username", read_only=True)
    job_post = serializers.SlugRelatedField(slug_field="id", read_only=True)
    milestone_status = serializers.ChoiceField(choices=MILESTONE_STATUS)

    class Meta:
        model = MilestoneV2
        fields = ["id", "user", "job_post", "name", "description", "time", "fund_released", "milestone_status",
                  "file", "completed_date", "completed_description", "created", "updated"]
        read_only_fields = ["job_post", "name", "description", "time", "fund_released", "file", "completed_date",
                            "completed_description", "created", "updated"]


class MilestoneV2UpdateCoderSerializer(serializers.ModelSerializer):
    MILESTONE_STATUS = (
        ('COMPLETE', 'Complete'),
        ('ACTIVE', 'Active'),
    )
    user = serializers.SlugRelatedField(slug_field="username", read_only=True)
    job_post = serializers.SlugRelatedField(slug_field="id", read_only=True)
    milestone_status = serializers.ChoiceField(choices=MILESTONE_STATUS)

    class Meta:
        model = MilestoneV2
        fields = ["id", "user", "job_post", "name", "description", "time", "fund_released", "milestone_status",
                  "file", "completed_date", "completed_description", "created", "updated"]
        read_only_fields = ["job_post", "name", "description", "time", "fund_released", "file", "completed_date",
                            "completed_description", "created", "updated"]


class ProposalV2Serializer(serializers.ModelSerializer):
    user = serializers.SlugRelatedField(slug_field="username", read_only=True)
    job_post = serializers.SlugRelatedField(slug_field="id", queryset=JobPostV2.objects.all())

    class Meta:
        model = JobProposalV2
        fields = ["id", "user", "job_post", "proposal_description", "proposal_type", "hourly_rate",
                  "availability_per_week", "attachment_1", "attachment_2", "attachment_3", "coder_fee",
                  "platform_fee", "platform_fee_percentage", "total_project_cost", "is_submitted", "estimate_time",
                  "status", "created", "updated"]
        read_only_fields = ["proposal_type", "coder_fee", "platform_fee", "platform_fee_percentage",
                            "total_project_cost", "is_submitted", "estimate_time", "status", "created", "updated"]

    def create(self, validated_data):
        job_post = validated_data.get('job_post', None)

        if job_post is not None:
            validated_data['proposal_type'] = job_post.budget_type
            if validated_data['proposal_type'] == "FIXED":
                validated_data['hourly_rate'] = None
                validated_data['availability_per_week'] = None
        return super().create(validated_data)

    def validate(self, attrs):
        job_post = attrs.get("job_post", None)
        proposal_type = job_post.budget_type
        hourly_rate = attrs.get("hourly_rate", None)

        # write code here to check if Milestones are added already for Fixed price job and raise validation error if
        # milestone for coder/job does not exist. Do not allow Job Proposal creation for Fixed price without atleast
        # 1 milestone

        if proposal_type == "HOURLY" and hourly_rate is None:
            raise ValidationError(
                {"hourly_rate": "Hourly rate cannot be None when proposal type is hourly.",
                 "availability_per_week": "Availability Per Week cannot be None when proposal type is hourly."})
        return attrs


class ProposalV2UpdateCoderSerializer(serializers.ModelSerializer):
    JOB_PROPOSAL_STATUS = (
        ('ACCEPTED_BY_CODER', 'Accepted by Coder'),
        ('REJECTED_BY_CODER', 'Rejected by Coder')
    )
    user = serializers.SlugRelatedField(slug_field="username", read_only=True)
    job_post = serializers.SlugRelatedField(slug_field="id", read_only=True)
    status = serializers.ChoiceField(choices=JOB_PROPOSAL_STATUS)

    class Meta:
        model = JobProposalV2
        fields = ["id", "user", "job_post", "proposal_description", "proposal_type", "hourly_rate",
                  "availability_per_week", "attachment_1", "attachment_2", "attachment_3", "coder_fee",
                  "platform_fee", "platform_fee_percentage", "total_project_cost", "is_submitted", "estimate_time",
                  "status", "created", "updated"]
        read_only_fields = ["job_post", "proposal_description", "proposal_type", "hourly_rate", "availability_per_week",
                            "attachment_1", "attachment_2", "attachment_3", "coder_fee", "platform_fee",
                            "platform_fee_percentage", "total_project_cost", "estimate_time", "status", "created",
                            "updated"]


class ProposalV2UpdateClientSerializer(serializers.ModelSerializer):
    JOB_PROPOSAL_STATUS = (
        ('ACCEPTED_BY_CLIENT', 'Accepted by Client'),
        ('REJECTED_BY_CLIENT', 'Rejected by Client'),
    )
    user = serializers.SlugRelatedField(slug_field="username", read_only=True)
    job_post = serializers.SlugRelatedField(slug_field="id", read_only=True)
    status = serializers.ChoiceField(choices=JOB_PROPOSAL_STATUS)

    class Meta:
        model = JobProposalV2
        fields = ["id", "user", "job_post", "proposal_description", "proposal_type", "hourly_rate",
                  "availability_per_week", "attachment_1", "attachment_2", "attachment_3", "coder_fee",
                  "platform_fee", "platform_fee_percentage", "total_project_cost", "is_submitted", "estimate_time",
                  "status", "created", "updated"]
        read_only_fields = ["job_post", "proposal_description", "proposal_type", "hourly_rate", "availability_per_week",
                            "attachment_1", "attachment_2", "attachment_3", "coder_fee", "platform_fee",
                            "platform_fee_percentage", "total_project_cost", "is_submitted", "estimate_time", "created",
                            "updated"]


class JobContractSerializer(serializers.ModelSerializer):
    coder_id = serializers.SlugRelatedField(slug_field='username', queryset=User.objects.all())
    client_id = serializers.SlugRelatedField(slug_field='username', queryset=User.objects.all())
    job_proposal = serializers.SlugRelatedField(slug_field='id', queryset=JobProposalV2.objects.all())

    class Meta:
        model = JobContract
        fields = ['id', 'coder_id', 'client_id', 'name', 'job_proposal', 'start_date', 'end_date', 'is_active', 
                  'feedback', 'total_amount_earned', 'total_hours_worked', 'hourly_rate', 'hirecoder_fee', 
                  'created', 'updated']

class TimesheetCoderSerializer(serializers.ModelSerializer):
    user = serializers.SlugRelatedField(slug_field="username", read_only=True)
    job_contract = serializers.SlugRelatedField(slug_field="id", queryset=JobContract.objects.all())
    hirecoder_fee = serializers.FloatField(source='job_contract.hirecoder_fee', read_only=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        coder_id = self.context['request'].user
        self.fields['job_contract'].queryset = JobContract.objects.filter(coder_id=coder_id)

    def validate(self, data):
        job_contract = data['job_contract']
        start_time = data['start_time']
        end_time = data['end_time']
        if start_time is None:
            raise ValidationError("Please enter the start time")
        if end_time is None:
            raise ValidationError("Please enter the end time")
        if end_time<=start_time:
            raise ValidationError("End time must be after start time")
        
        budget_type = job_contract.job_proposal.job_post.budget_type
        if budget_type == "FIXED":
            raise ValidationError("Timesheet submission is only permitted for HOURLY budget jobs")
        elif budget_type == "HOURLY":
            print("Start time")
            print(data['date'])
            start_hours = start_time.hour + start_time.minute/60
            end_hours = end_time.hour + end_time.minute/60
            total_hours = end_hours - start_hours
            total_hours = round(total_hours, 2)
            amount = total_hours * job_contract.hourly_rate
            data['total_hours'] = total_hours
            data['amount'] = amount

            client_user = job_contract.job_proposal.job_post.user
            data['user'] = client_user.username

        return data
    
    class Meta:
        model = Timesheet
        fields = ['id', 'user', 'job_contract', 'date','start_time', 'end_time', 
                  'description', 'total_hours', 'amount', 'hirecoder_fee', 'payment_status', 'timesheet_status', 
                  'created', 'updated']
        read_only_fields = ['user', 'total_hours', 'amount', 'payment_status', 'timesheet_status',
                            'created', 'updated', 'hirecoder_fee']   
        

class TimesheetClientSerializer(serializers.ModelSerializer):
    user = serializers.SlugRelatedField(slug_field="username", read_only=True)
    job_contract = serializers.SlugRelatedField(slug_field="id", read_only=True)
    hirecoder_fee = serializers.FloatField(source='job_contract.hirecoder_fee', read_only=True)

    
    def update(self, instance, validated_data):
        if len(validated_data)>1 or 'timesheet_status' not in validated_data:
            raise ValidationError("Client can only update the timesheet status")
        else:
            if instance.timesheet_status == "APPROVED":
                raise ValidationError("Not permitted to update status of approved timesheet")
            else:
                return super().update(instance, validated_data)
    
    class Meta:
        model = Timesheet
        fields = ['id', 'user', 'job_contract', 'date','start_time', 'end_time', 
                  'description', 'total_hours', 'amount', 'hirecoder_fee', 'payment_status', 'timesheet_status', 
                  'created', 'updated']
        read_only_fields = ['user', 'job_contract','date','start_time', 'end_time', 
                            'description','total_hours', 'amount', 'payment_status', 
                            'created', 'updated']  

