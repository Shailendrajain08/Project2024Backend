import pytz
from datetime import datetime
from rest_framework import serializers
from core.models import JobPost, TimeZone, Expertise
from accounts.models import User, Technology, Skill, CoderSkillsExperience, Address
from .models import TermsAndConditions


class RecommendedJobsSerializer(serializers.ModelSerializer):
    user = serializers.SlugRelatedField(slug_field="username", read_only=True)
    company_name = serializers.SerializerMethodField()
    company_logo = serializers.SerializerMethodField()
    

    class Meta:
        model = JobPost
        fields = [
            "id",
            "user",
            "title",
            "description",
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
            'company_name',
            'company_logo'
        ]
        read_only_fields = fields

    def get_company_name(self, instance):
        if hasattr(instance.user, 'companydetails'):
            return instance.user.companydetails.company_name
        
    def get_company_logo(self, instance):
        if hasattr(instance.user, 'companydetails') and instance.user.companydetails.logo:
            return instance.user.companydetails.logo.url

    def to_representation(self, instance):
        representation = super().to_representation(instance)

        technology_data = instance.technologies.all().values("id", "name", "is_approved")
        representation["technology"] = list(technology_data)

        timezone_data = instance.timezone.values_list("id", flat=True)
        formatted_timezones = [
            f"GMT{pytz.timezone(TimeZone.objects.get(id=timezone_id).name).localize(datetime.now()).strftime('%z')[:-2]}:00 {TimeZone.objects.get(id=timezone_id).name}"
            for timezone_id in timezone_data
        ]

        representation["timezone"] = formatted_timezones

        expertise_data = instance.expertise.values_list("expertise", flat=True)
        representation["expertise"] = expertise_data

        return representation        


class UserTechnologySerializer(serializers.ModelSerializer):
    class Meta:
        model = Technology
        fields = ['id', 'name']


class UserSkillSerializer(serializers.ModelSerializer):
    technology = UserTechnologySerializer()
    
    class Meta:
        model = Skill
        fields = ['technology', 'years_of_experience', 'skill_type', 'expertise_level']


class UserSkillsExperienceSerializer(serializers.ModelSerializer):
    skills = serializers.SerializerMethodField()
    
    class Meta:
        model = CoderSkillsExperience
        fields = ['skills', 'hourly_rate', 'identity', "total_years_of_experience", "profile_picture",]
        
    def get_skills(self, instance):
        skills_queryset = Skill.objects.filter(user=instance.user)
        serializer = UserSkillSerializer(skills_queryset, many=True)
        return serializer.data

   
class UserAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = ['city', 'country']        

       
class RecommendedCoderSerializer(serializers.ModelSerializer):
    id = serializers.CharField(source='username')
    chat_id = serializers.CharField(default=None, read_only=True)
    coderskillexperience = UserSkillsExperienceSerializer(source='coderskillsexperience')
    address = UserAddressSerializer()
    created = serializers.DateTimeField(source='date_joined')
    updated = serializers.DateTimeField(default=None, read_only=True)
        
    class Meta:
        model = User
        fields = ['id', 'chat_id', 'first_name', 'last_name', 'coderskillexperience', 'address', 'created', 'updated']


class TermsAndConditionsSerializer(serializers.ModelSerializer):
    class Meta:
        model = TermsAndConditions
        fields = ['id', 'content', 'created', 'updated']

    def validate(self, value):
        if self.context["request"].method == "POST":
            if TermsAndConditions.objects.exists():
                raise serializers.ValidationError(
                    "Terms and conditions object already exists. Update it instead of creating a new one.")
        return value
