from django.contrib.auth import get_user_model
from django.contrib.auth import authenticate
from django.core.validators import RegexValidator
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.password_validation import validate_password
from django.utils.http import urlsafe_base64_decode as uid_decoder
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import force_str
from rest_framework.exceptions import AuthenticationFailed
from .models import (
    Technology,
    User,
    Agency,
    CompanyDetails,
    Degree,
    Certification,
    EducationalQualification,
    Address,
    DigitalPresence,
    Skill,
    CoderSkillsExperience,
)  # noqa: E501
from core.models import JobPost
from .utils import ValidationUtils
from mysite.settings import MAX_DEGREE, MAX_CERTIFICATE
from typing import Any, Dict
from rest_framework_simplejwt.settings import api_settings

UserModel = get_user_model()


USER_ROLE_CHOICES = (
    ("CLIENT", "Client"),
    ("CODER", "Coder"),
    ("COWORKER", "Coworker"),
    ("SUCCESS-MANAGER", "Success Manager"),
)

class AgencySerializer(serializers.ModelSerializer):
    class Meta:
        model = Agency
        fields = [
            "id",
            "name",
            "website",
            "phone",
            "email",
            "address_line_1",
            "address_line_2",
            "country",
            "city",
            "state",
            "zip_code",
            "created",
            "updated",
        ]  # noqa : E501
        read_only_fields = [
            "created",
            "updated",
        ]


class RegisterSerializer(serializers.ModelSerializer):
    phone_regex = RegexValidator(
        regex=r"^\+?1?\d{10,14}$",
        message="Enter Phone Number in the format +1. Upto 15 digits allowed",
    )
    phone = serializers.CharField(
        validators=[phone_regex], max_length=15, required=True
    )
    password = serializers.CharField(
        write_only=True,
        validators=[validate_password],
        style={"input_type": "password"},
    )  # noqa:  E501

    confirm_password = serializers.CharField(
        write_only=True, style={"input_type": "password"}
    )  # noqa:  E501

    class Meta:
        model = User
        fields = [
            "first_name",
            "last_name",
            "email",
            "phone",
            "password",  # to be hashed
            "confirm_password",
            "role",
            "type",
            "tc",
            "username",
            "agency",
        ]
        read_only_fields = ["username"]
        # # extra_kwargs = {
        #     "password": {
        #         "write_only": True,
        #         "style": {"input_type": "password"},
        #     },  # noqa: E501
        # }

    def validate(self, attrs):
        tc = attrs.get("tc", "")
        if not tc:
            raise serializers.ValidationError(
                "Please accept the terms and conditions."
            )  # noqa:  E501

        password = attrs.get("password")
        confirm_password = attrs.get("confirm_password")

        if password != confirm_password:  # noqa:  E501
            raise serializers.ValidationError("Passwords do not match.")

        role = attrs.get("role", "")
        user_type = attrs.get("type", "")
        agency = attrs.get("agency", None)

        if role == "CLIENT" and user_type == "AGENCY":
            raise serializers.ValidationError(
                "A client cannot be associated with an agency."
            )
        elif role == "CODER" and user_type == "AGENCY" and agency is None:
            raise serializers.ValidationError(
                "Agency field is required for a coder with type 'AGENCY'."
            )

        if user_type == "INDIVIDUAL" and agency is not None:
            raise serializers.ValidationError(
                "Agency field should not be provided for individual users."
            )

        return attrs

    def create(self, validated_data):
        validated_data.pop("confirm_password", None)
        password = validated_data.pop("password")
        user = User.objects.create(**validated_data)
        user.set_password(password)
        user.save()
        return user


class LoginSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=False)
    role = serializers.ChoiceField(
        choices=USER_ROLE_CHOICES, required=True
    )  # noqa : E501

    class Meta:
        model = User
        fields = ["email", "password", "role"]
        extra_kwargs = {
            "password": {
                "write_only": True,
                "style": {"input_type": "password"},
            },  # noqa: E501
        }

    def validate(self, validate_data):
        email = validate_data.get("email")
        password = validate_data.get("password")
        role = validate_data.get("role")
        if email and password and role:
            user = authenticate(
                request=self.context.get("request"),
                email=email,
                password=password,
                role=role,  # noqa: 501
            )
            try:
                registered_user = User.objects.get(email=email)
            except User.DoesNotExist:
                raise serializers.ValidationError(
                    "Unable to log in with provided credentials."
                )

            if not registered_user.is_active:
                raise serializers.ValidationError("User account is disabled.")

            if role != registered_user.role:
                raise serializers.ValidationError(
                    "Unable to log in with provided credentials."
                )  # noqa : E501
            if user:
                if not user.is_email_verified:
                    raise serializers.ValidationError("Email is not verified.")
            else:
                raise serializers.ValidationError(
                    "Unable to log in with provided credentials."
                )

            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)
            refresh_token = str(refresh)

        else:
            raise serializers.ValidationError(
                "Both email and password are required"
            )  # noqa: 501

        validate_data["access_token"] = access_token
        validate_data["refresh_token"] = refresh_token
        validate_data["user"] = registered_user
        return validate_data


class VerifyEmailSerializer(serializers.Serializer):
    token = serializers.CharField(write_only=True)


class TechnologySerializer(serializers.ModelSerializer):
    user = serializers.SlugRelatedField(slug_field="username", read_only=True)

    class Meta:
        model = Technology
        fields = ["id", "name", "user", "is_approved", "created", "updated"]
        read_only_fields = ["user", "is_approved", "created", "updated"]

    def validate_name(self, value):
        value = value.lower()
        if Technology.objects.filter(name=value):
            raise serializers.ValidationError("Technology already exists!")
        return value


class CoderAddressSerializer(serializers.ModelSerializer):

    user = serializers.SlugRelatedField(slug_field="username", read_only=True)

    class Meta:
        model = Address
        fields = [
            "id", "user", "address_line_1", "address_line_2", "country", "city", "state", "zip_code",
            "created", "updated"
        ]
        extra_kwargs = {
            "country": {"required": True},
            "address_line_1": {"required": True},
            "state": {"required": True},
            "city": {"required": True},
            "zip_code": {"required": True},
        }
        read_only_fields = ["created", "updated"]

    def validate_country(self, value):
        if not value or value == "":
            raise serializers.ValidationError("Country is required and can't be left empty.")
        return value

    def validate_address_line_1(self, value):
        if not value or value == "":
            raise serializers.ValidationError("Address Line 1 is required and can't be empty.")
        return value

    def validate_state(self, value):
        if not value or value == "":
            raise serializers.ValidationError("State is required and can't be left empty.")
        return value

    def validate_city(self, value):
        if not value or value == "":
            raise serializers.ValidationError("City is required and can't be left empty.")
        return value

    def validate_zip_code(self, value):
        if not value and value == "":
            raise serializers.ValidationError("Zip code is reuqired and can't be left empty.")
        return value

    def validate(self, validated_data):
        """
        we are adding this validation as django is failing to validate on model level
        """
        user = self.context["request"].user
        if (
            self.context["request"].method == "POST"
            and Address.objects.filter(user=user).exists()
        ):
            raise serializers.ValidationError(
                "Address details for this user already exists."
            )
        return validated_data


class ClientAddressSerializer(serializers.ModelSerializer):

    user = serializers.SlugRelatedField(slug_field="username", read_only=True)

    class Meta:
        model = Address
        fields = [
            "id",
            "user",
            "address_line_1",
            "address_line_2",
            "country",
            "city",
            "state",
            "zip_code",
            "created",
            "updated",
        ]
        read_only_fields = ["created", "updated"]

    def validate(self, validated_data):
        """
        we are adding this validation as django is failing to validate on model level
        """
        user = self.context["request"].user
        if (
            self.context["request"].method == "POST"
            and Address.objects.filter(user=user).exists()
        ):
            raise serializers.ValidationError(
                "Address details for this user already exists."
            )
        return validated_data


class ResendEmailVerificationSerializer(serializers.Serializer):
    email = serializers.EmailField(write_only=True, required=True)


class CompanyDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = CompanyDetails
        fields = [
            "id",
            "company_name",
            "company_website",
            "linkedin_url",
            "logo",
            "created",
            "updated",
        ]
        read_only_fields = ["created", "updated"]

    def validate(self, validate_data):
        """
        we are adding this validation as django is failing to validate on model level
        """
        user = self.context["request"].user
        if (
            self.context["request"].method == "POST"
            and CompanyDetails.objects.filter(user=user).exists()
        ):
            raise serializers.ValidationError(
                "Company details for this user already exists."
            )
        return validate_data


class PasswordChangeSerializer(serializers.Serializer):
    old_password = serializers.CharField(
        write_only=True, style={"input_type": "password"},  
        required=True, error_messages={
            "required": "Old password is required."},)
    new_password1 = serializers.CharField(
        write_only=True, validators=[validate_password], style={"input_type": "password"},
        required=True, error_messages={
            "required": "New password is required.", "blank": "New password cannot be blank.", },)
    new_password2 = serializers.CharField(
        write_only=True, style={"input_type": "password"},
        required=True, error_messages={
            "required": "Confirmation of the new password is required.",
            "blank": "Confirmation of the new password cannot be blank.", },)
    
    def validate_new_password1(self, value):
        old_password = self.initial_data.get("old_password", None)

        if old_password == value:
            raise serializers.ValidationError("You cannot set Old password as New password")

        return value

    def validate_new_password2(self, value):
        new_password1 = self.initial_data.get("new_password1", None)

        if new_password1 != value:
            raise serializers.ValidationError("Passwords do not match.")

        return value

    def change_password(self, user):
        old_password = self.validated_data["old_password"]
        new_password1 = self.validated_data["new_password1"]

        if not user.check_password(old_password):
            raise serializers.ValidationError({"old_password": ["Old password is incorrect."]})

        user.set_password(new_password1)
        user.save()


class PasswordResetSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)


class SetNewPasswordSerializer(serializers.Serializer):
    password = serializers.CharField(write_only=True, validators=[validate_password], style={"input_type": "password"},) 
    confirm_password = serializers.CharField(write_only=True, style={"input_type": "password"})
    token = serializers.CharField(write_only=True, required=True)
    uidb64 = serializers.CharField(write_only=True, required=True)

    class Meta:
        fields = ["password", "confirm_password", "token", "uidb64"]

    def validate(self, attrs):
        password = attrs.get("password", None)
        token = attrs.get("token", None)
        uidb64 = attrs.get("uidb64", None)
        confirm_password = attrs.get("confirm_password", None)
        if password != confirm_password:
            raise AuthenticationFailed("Password & Confirm Password do not match.", 400)
        try:
            id = force_str(uid_decoder(uidb64))
            user = User.objects.get(id=id)
        except Exception:
            raise AuthenticationFailed("The reset link is invalid", 400)
        if not PasswordResetTokenGenerator().check_token(user, token):
            raise AuthenticationFailed("The reset link is invalid", 400)
        user.set_password(password)
        user.save()
        return user


class SkillSerializer(serializers.ModelSerializer):
    technology = serializers.SlugRelatedField(
        slug_field="id", queryset=Technology.objects.all()
    )
    user = serializers.SlugRelatedField(slug_field="username", read_only=True)

    class Meta:
        model = Skill
        fields = [
            "id",
            "user",
            "technology",
            "years_of_experience",
            "skill_type",
            "expertise_level",
            "created",
            "updated",
        ]
        read_only_fields = ["user", "created", "updated"]
 
    def validate(self, validated_data):
        request = self.context["request"]
        if request.method in ["PUT", "POST"] and "skill_type" not in validated_data:
            raise serializers.ValidationError("skill_type is required")

        return validated_data

    def validate_technology(self, value):
        user = self.context["request"].user
        request = self.context["request"]
        if request.method in ["POST"] and Skill.objects.filter(user=user, technology=value).exists():
            raise serializers.ValidationError(f"A skill with technology '{value}' already exists for the current user.")

        elif request.method in ["PUT", "PATCH"]:
            if self.instance:
                if Skill.objects.filter(user=user, technology=value).exclude(id=self.instance.id).exists():
                    raise serializers.ValidationError(f"A skill with technology '{value}' already exists for the current user.")

        return value

    def validate_skill_type(self, value):
        user = self.context["request"].user
        existing_skills = Skill.objects.filter(user=user)
        requested_skill_type = value
        request = self.context["request"]

        if request.method == "POST":
            if requested_skill_type == "PRIMARY" and existing_skills.filter(skill_type="PRIMARY").exists():
                raise serializers.ValidationError("User can only have one primary skill.")

            elif requested_skill_type == "SECONDARY" and existing_skills.filter(skill_type="SECONDARY").exists():
                raise serializers.ValidationError("User can only have one secondary skill.")

            elif requested_skill_type == "OTHER" and existing_skills.filter(skill_type="OTHER").count() >= 10:
                raise serializers.ValidationError("User can have at most 10 other skills.")

        elif request.method in ["PUT", "PATCH"]:
            if self.instance:
                if requested_skill_type == "PRIMARY" and existing_skills.filter(skill_type="PRIMARY").exclude(id=self.instance.id).exists():
                    raise serializers.ValidationError("User can only have one primary skill.")
                elif requested_skill_type == "SECONDARY" and existing_skills.filter(skill_type="SECONDARY").exclude(id=self.instance.id).exists():
                    raise serializers.ValidationError("User can only have one secondary skill.")

                elif requested_skill_type == "OTHER" and existing_skills.filter(skill_type="OTHER").exclude(id=self.instance.id).count()>= 10:
                    raise serializers.ValidationError("User can have at most 10 other skills.")

        return value


class CoderSkillsExperienceSerializer(serializers.ModelSerializer):
    user = serializers.SlugRelatedField(slug_field="username", read_only=True)
    skills = serializers.SerializerMethodField()

    class Meta:
        model = CoderSkillsExperience
        fields = [
            "id",
            "user",
            "introduction",
            "total_years_of_experience",
            "identity",
            "hourly_rate",
            "brief_work_experience",
            "profile_picture",
            "skills",
            "created",
            "updated",
        ]
        read_only_fields = ["user", "created", "updated"]

    def get_skills(self, instance):
        skills_queryset = Skill.objects.filter(user=instance.user)
        serializer = SkillSerializer(skills_queryset, many=True)
        return serializer.data

    def validate(self, validate_data):
        """
        we are adding this validation as django is failing to validate on model level
        """
        user = self.context["request"].user
        request = self.context["request"]
        if request.method == "POST" and CoderSkillsExperience.objects.filter(user=user).exists():
            raise serializers.ValidationError("Skills and Experience for this user already exists.")
        return validate_data


class CoderDigitalPresenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = DigitalPresence
        fields = [
            "id",
            "linkedin_url",
            "github_url",
            "stackoverflow_url",
            "created",
            "updated",
        ]
        read_only_fields = ["created", "updated"]

    def validate_linkedin_url(self, value):
        return ValidationUtils.validate_custom_url(value, "linkedin")

    def validate_github_url(self, value):
        return ValidationUtils.validate_custom_url(value, "github")

    def validate_stackoverflow_url(self, value):
        return ValidationUtils.validate_custom_url(value, "stackoverflow")

    def validate(self, validate_data):
        """
        we are adding this validation as django is failing to validate on model level
        """
        user = self.context["request"].user
        if (
            self.context["request"].method == "POST"
            and DigitalPresence.objects.filter(user=user).exists()
        ):
            raise serializers.ValidationError(
                "Digital Presence for this user already exists."
            )
        return validate_data

    def validate_linkedin_url(self, value):
        return ValidationUtils.validate_custom_url(value, "linkedin")

    def validate_github_url(self, value):
        return ValidationUtils.validate_custom_url(value, "github")

    def validate_stackoverflow_url(self, value):
        return ValidationUtils.validate_custom_url(value, "stackoverflow")
     

class ClientDigitalPresenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = DigitalPresence
        fields = [
            "id",
            "glassdoor_url",
            "career_bliss_url",
            "youtube_url",
            "other_social_url",
            "created",
            "updated",
        ]
        read_only_fields = ["created", "updated"]

    def validate(self, validate_data):
        """
        we are adding this validation as django is failing to validate on model level
        """
        user = self.context["request"].user
        if (
            self.context["request"].method == "POST"
            and DigitalPresence.objects.filter(user=user).exists()
        ):
            raise serializers.ValidationError(
                "Digital Presence for this user already exists."
            )
        return validate_data

    def validate_glassdoor_url(self, value):
        return ValidationUtils.validate_custom_url(value, "glassdoor")

    def validate_career_bliss_url(self, value):
        return ValidationUtils.validate_custom_url(value, "careerbliss")

    def validate_youtube_url(self, value):
        return ValidationUtils.validate_custom_url(value, "youtube")


class CertificationSerializer(serializers.ModelSerializer):
    """
    Serializer for the Certificate model.

    Attributes:
        validate_certificate_name: Custom validation for the certificate name field.
    """
    class Meta:
        model = Certification
        fields = [
            "id",
            "certificate_name",
            "year_of_completion",
            "created",
            "updated",
        ]
        read_only_fields = ["created", "updated"]
        
    def validate_certificate_name(self, value):
        user = self.context["request"].user
        request = self.context["request"]
        
        if request.method == "POST":
            existing_certificates_count = Certification.objects.filter(user=user).count()
            certificate_exists = Certification.objects.filter(user=user, certificate_name__iexact=value).exists()
            if certificate_exists:
                raise serializers.ValidationError(f"A certificate with the name {value} already exists for the user.")
            if existing_certificates_count >= MAX_CERTIFICATE:
                raise serializers.ValidationError(f"Cannot add more than {MAX_CERTIFICATE} certificates.")
        return value


class DegreeSerializer(serializers.ModelSerializer):
    """
    Serializer for the Degree model.

    Attributes:
        validate_degree: Custom validation for the degree field.
    """
    class Meta:
        model = Degree
        fields = [
            "id",
            "university",
            "passing_year",
            "degree",
            "college",
            "created",
            "updated",
        ]
        read_only_fields = ["created", "updated"]

    def validate_degree(self, value):
        user = self.context["request"].user
        request = self.context["request"]

        if request.method == "POST":
            existing_degrees_count = Degree.objects.filter(user=user).count()
            degree_exists = Degree.objects.filter(user=user, degree__iexact=value).exists()

            if degree_exists:
                raise serializers.ValidationError(f"A degree with the name {value} already exists for the user.")

            if existing_degrees_count >= MAX_DEGREE:
                raise serializers.ValidationError(f"Cannot add more than {MAX_DEGREE} degrees.")
        return value


class EducationalQualificationSerializer(serializers.ModelSerializer):
    """
    Serializer for the Education model.

    Attributes:
        qualifications: SerializerMethodField to retrieve qualifications associated with the education.
        certificates: SerializerMethodField to retrieve certificates associated with the education.
        user: SlugRelatedField to represent the associated user's username.

    Methods:
        get_qualifications: Retrieve and serialize qualifications associated with the education.
        get_certificates: Retrieve and serialize certificates associated with the education.
        validate: Custom validation to check if education and qualification details already exist for the user.

    """
    degrees = serializers.SerializerMethodField()
    certificates = serializers.SerializerMethodField()
    user = serializers.SlugRelatedField(slug_field="username", read_only=True)

    class Meta:
        model = EducationalQualification
        fields = [
            "id",
            "user",
            "certificates",
            "degrees",
            "resume",
            "portfolio",
            "created",
            "updated",
        ]
        read_only_fields = ["user", "created", "updated"]

    def get_degrees(self, instance):
        degree_queryset = Degree.objects.filter(user=instance.user)
        serializer = DegreeSerializer(degree_queryset, many=True)
        return serializer.data

    def get_certificates(self, instance):
        certificate_queryset = Certification.objects.filter(user=instance.user)
        serializer = CertificationSerializer(certificate_queryset, many=True)
        return serializer.data

    def validate_resume(self, resume):
        """
        Custom validation for the resume field.
        """
        if resume is not None:
            max_file_size = 5 * 1024 * 1024
            allowed_formats = ['pdf', 'doc', 'docx', "txt", "jpg", "jpeg", "png"]

            if resume.size > max_file_size:
                raise serializers.ValidationError("File size is too large. Maximum allowed size is 5 MB.")

            file_extension = resume.name.split('.')[-1].lower()
            if file_extension not in allowed_formats:
                raise serializers.ValidationError(
                    "Invalid file format. Allowed formats: pdf, doc, docx, txt, jpg, jpeg, png ")

        return resume

    def validate(self, validate_data):
        """
        we are adding this validation as django is failing to validate on model level
        """
        user = self.context["request"].user
        request = self.context["request"]
        if request.method == "POST" and EducationalQualification.objects.filter(user=user).exists():
            raise serializers.ValidationError("Education and Qualification details for this user already exists.")
        return validate_data


class CustomTokenRefreshSerializer(serializers.Serializer):
    refresh_token = serializers.CharField()
    access_token = serializers.CharField(read_only=True)
    token_class = RefreshToken

    def validate(self, attrs: Dict[str, Any]) -> Dict[str, str]:
        refresh = self.token_class(attrs["refresh_token"])

        data = {"access_token": str(refresh.access_token)}

        if api_settings.ROTATE_REFRESH_TOKENS:
            if api_settings.BLACKLIST_AFTER_ROTATION:
                try:
                    # Attempt to blacklist the given refresh token
                    refresh.blacklist()
                except AttributeError:
                    # If blacklist app not installed, `blacklist` method will
                    # not be present
                    pass

            refresh.set_jti()
            refresh.set_exp()
            refresh.set_iat()

            data["refresh"] = str(refresh)

        return data


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "username",
            "first_name",
            "last_name",
            "email",
            "phone",
            "role",
            "type",
            "tc",
            "is_profile_complete",
            "profile_completeness_percentage",
        ]


class UserCertificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Certification
        fields = ['certificate_name', 'year_of_completion']

        
class UserDegreeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Degree
        fields = ['university', 'passing_year', 'degree', 'college']


class UserEducationSerializer(serializers.ModelSerializer):        
    degrees = serializers.SerializerMethodField()
    certificates = serializers.SerializerMethodField()

    class Meta:
        model = EducationalQualification
        fields = [
            "certificates",
            "degrees",
            "resume",
            "portfolio",  
        ]
        
        
    def get_degrees(self, instance):
        degree_queryset = Degree.objects.filter(user=instance.user)
        serializer = UserDegreeSerializer(degree_queryset, many=True)
        return serializer.data

    def get_certificates(self, instance):
        certificate_queryset = Certification.objects.filter(user=instance.user)
        serializer = UserCertificationSerializer(certificate_queryset, many=True)
        return serializer.data
    
       
class FeedbackSerializer(serializers.Serializer):
    rating = serializers.IntegerField(allow_null=True)
    comment = serializers.CharField(allow_null=True)
    

class CompletedJobSerializer(serializers.Serializer):
    title = serializers.CharField(allow_null=True)
    start_date = serializers.DateField(allow_null=True)
    end_date = serializers.DateField(allow_null=True)
    feedback = FeedbackSerializer(many=True, allow_null=True, default=[{}])
    total_amount_earned = serializers.FloatField(allow_null=True)
    total_hours_worked = serializers.FloatField(allow_null=True)
    hourly_rate = serializers.FloatField(allow_null=True)
    
    
class UserTechnologySerializer(serializers.ModelSerializer):
    class Meta:
        model = Technology
        fields = ['id', 'name']


class UserSkillSerializer(serializers.ModelSerializer):
    technology = UserTechnologySerializer()

    class Meta:
        model = Skill
        fields = ['technology', 'years_of_experience', 'skill_type', 'expertise_level']



class CoderSerializer(serializers.ModelSerializer):
    id = serializers.CharField(source='username')
    completed_jobs = CompletedJobSerializer(many=True, allow_null=True, default=[{}])
    skill_and_experience = CoderSkillsExperienceSerializer(source='coderskillsexperience')
    linkedin_url = serializers.URLField(source='digitalpresence.linkedin_url')
    github_url = serializers.URLField(source='digitalpresence.github_url')
    stackoverflow_url = serializers.URLField(source='digitalpresence.stackoverflow_url')
    country = serializers.CharField(source='address.country')
    city = serializers.CharField(source='address.city')
    state = serializers.CharField(source='address.state')
    educational_qualification = UserEducationSerializer(many=True, source='educationalqualification_set')
    is_favorite = serializers.BooleanField(default=False)
    past_employment_history = serializers.ListSerializer(
        child=serializers.DictField(), allow_empty=True, allow_null=True)
   
    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'email', 'phone', 'type', 'agency', 'is_favorite', 
                  'skill_and_experience', 'linkedin_url', 'github_url', 'country', 'stackoverflow_url', 'city', 
                  'state', 'date_joined', 'educational_qualification', 'past_employment_history', 'completed_jobs']
    
class ClientSerializer(serializers.ModelSerializer):
    id = serializers.CharField(source='username')
    company_name = serializers.CharField(source = 'companydetails.company_name')
    company_website = serializers.URLField(source = 'companydetails.company_website')
    logo = serializers.ImageField(source='companydetails.logo')
    linkedin_url = serializers.URLField(source = 'digitalpresence.linkedin_url')
    glassdoor_url = serializers.URLField(source = 'digitalpresence.glassdoor_url')
    youtube = serializers.CharField(source = 'digitalpresence.youtube_url')
    careerbliss = serializers.URLField(source = 'digitalpresence.career_bliss_url')
    country = serializers.CharField(source = 'address.country')
    city = serializers.CharField(source = 'address.city')
    state = serializers.CharField(source = 'address.state')
    job_posted = serializers.SerializerMethodField()
    total_spent = serializers.IntegerField(default=20000)
    average_hourly_rate = serializers.SerializerMethodField()
    company_size = serializers.CharField(default=None)
    is_payment_method_verified = serializers.BooleanField(default=False)
    reviews = serializers.IntegerField(default=4)
    count_of_active_projects = serializers.SerializerMethodField()
    count_of_hired_coders = serializers.SerializerMethodField()

    def get_job_posted(self, obj):
        return JobPost.objects.filter(user=obj.id).count()
    
    def get_average_hourly_rate(self, obj):
        # return JobContract.objects.filter(user=obj, job_proposal__is_hourly_rate=True).aggregate(Avg('job_proposal__hourly_rate'))['job_proposal__hourly_rate__avg']
        return None
    
    def get_count_of_active_projects(self, obj):
        return JobPost.objects.filter(user=obj, status='ACTIVE').count()
    
    def get_count_of_hired_coders(self, obj):
        # return JobContract.objects.filter(user=obj).count()
        return None
    
    class Meta:
        model = User
        fields = ['id','first_name', 'last_name', 'email', 'company_name', 'company_website',
                  'logo','linkedin_url', 'glassdoor_url', 'youtube', 'careerbliss', 'phone',
                  'country', 'city', 'state', 'role', 'job_posted', 'total_spent', 'average_hourly_rate',
                  'company_size', 'is_payment_method_verified', 'reviews', 'count_of_active_projects',
                  'count_of_hired_coders', 'date_joined']
