from django.contrib.sites.models import Site
from django.urls import reverse
from rest_framework.permissions import AllowAny
from datetime import datetime, timedelta
from django.core.cache import cache
from rest_framework import viewsets
from .serializers import (
    RegisterSerializer,
    VerifyEmailSerializer,
    TechnologySerializer,
    AgencySerializer,
    LoginSerializer,
    CoderAddressSerializer,
    ClientAddressSerializer,
    ResendEmailVerificationSerializer,
    CompanyDetailsSerializer,
    SetNewPasswordSerializer,
    PasswordResetSerializer,
    PasswordChangeSerializer,
    SkillSerializer,
    CoderSkillsExperienceSerializer,
    ClientDigitalPresenceSerializer,
    CoderDigitalPresenceSerializer,
    CertificationSerializer,
    DegreeSerializer,
    EducationalQualificationSerializer,
    CustomTokenRefreshSerializer,
    UserSerializer,
    CoderSerializer,
    ClientSerializer
)
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework.response import Response
from rest_framework import status
from .permissions import (
    IsClientOrCoderPermission,
    IsClientOrReadOnly,
    IsEmailVerified,
    IsCoder,
    IsClientOrCoder,
)  # noqa: E501
from rest_framework.permissions import IsAuthenticated
from .models import (
    User,
    Technology,
    Agency,
    CompanyDetails,
    Address,
    DigitalPresence,
    Skill,
    CoderSkillsExperience,
    Certification,
    Degree,
    EducationalQualification,
)  # noqa: E501
import jwt
from mysite.settings import SECRET_KEY
from . import filters
from django_filters.rest_framework import DjangoFilterBackend
from .utils import Util
from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site
from .utils import EmailUtil
from rest_framework import status
from .filters import CoderFilter


class AgencyViewSet(viewsets.ModelViewSet):
    queryset = Agency.objects.all()
    serializer_class = AgencySerializer
    permission_classes = [AllowAny]
    http_method_names = ["get", "post", "head", "options"]


class RegisterViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    http_method_names = ["post", "head", "options"]

    def create(self, request):
        user_data = request.data
        serializer = self.get_serializer(data=user_data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        user = User.objects.get(email=user_data["email"])
        refresh = RefreshToken.for_user(user)
        access_token = refresh.access_token
        
        response_data = {
            "access_token": str(access_token),
            "refresh_token": str(refresh),
            "user": serializer.data,
        }

        headers = self.get_success_headers(serializer.data)
        return Response(
            response_data, status=status.HTTP_201_CREATED, headers=headers
        )  # noqa:  E501


class VerifyEmailViewSet(viewsets.ModelViewSet):
    serializer_class = VerifyEmailSerializer
    queryset = User.objects.all()
    http_method_names = ["post", "head", "options"]

    def create(self, request):
        user_data = request.data
        serializer = self.get_serializer(data=user_data)
        serializer.is_valid(raise_exception=True)
        token = serializer.validated_data["token"]
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            user = User.objects.get(id=payload["user_id"])
            if not user.is_email_verified:
                user.is_email_verified = True
                user.save()
            return Response(
                {"email": "Successfully activated."}, status=status.HTTP_200_OK
            )
        except jwt.ExpiredSignatureError:
            return Response(
                {"error": "Activation Link Expired."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except jwt.exceptions.DecodeError:
            return Response(
                {"error": "Invalid Token"}, status=status.HTTP_400_BAD_REQUEST
            )  # noqa:  E501


class ResendEmailVerificationViewSet(viewsets.ModelViewSet):
    serializer_class = ResendEmailVerificationSerializer
    http_method_names = ["post", "head", "options"]
    rate_limit_seconds = settings.RATE_LIMIT_SECONDS
    verification_timeout_minutes = settings.VERIFICATION_TIMEOUT_MINUTES
    token_timeout_minutes = settings.TOKEN_TIMEOUT_MINUTES

    def create(self, request, *args, **kwargs):
        email = request.data.get("email")
        user_cache_key = f"verification_request_{email}"

        # Check if a request has been made recently
        last_request_time = cache.get(user_cache_key)
        if last_request_time:
            time_since_last_request = datetime.now() - last_request_time
            if time_since_last_request < timedelta(
                seconds=self.rate_limit_seconds
            ):  # noqa : E501
                wait_time = (
                    self.rate_limit_seconds
                    - time_since_last_request.total_seconds()  # noqa : E501
                )
                return Response(
                    {
                        "detail": f"Please wait for {wait_time:.0f} seconds before sending another request."  # noqa : E501
                    },
                    status=status.HTTP_429_TOO_MANY_REQUESTS,
                )

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response(
                {"detail": "Email verification link has been resent"},
                status=status.HTTP_201_CREATED,  # noqa : E501
            )

        if user.is_email_verified:
            return Response(
                {"detail": "User is already verified"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        token = RefreshToken.for_user(user).access_token
        absurl = f"https://ui-main.hirecoder.info/register?redirecturl=verify-email/token={str(token)}"

        email_body = f"Hi {user.first_name}, please use the link below to verify your email:\n{absurl}"  # noqa : E501
        data = {
            "email_body": email_body,
            "to_email": user.email,
            "email_subject": "Resend Email Verification",
        }
        try:
            send_status = Util.send_email(data)
        except Exception as e:
            obj = {
                    "message": f"Error occurred while sending verification email. {e}",
            }
            return Response(
                    obj,
                    status=status.HTTP_424_FAILED_DEPENDENCY,
                )

        # Update the timestamp for the last request
        cache.set(user_cache_key, datetime.now(), self.rate_limit_seconds)

        # Set a timeout for the verification link
        verification_cache_key = f"verification_link_{email}"
        cache.set(
            verification_cache_key,
            token,
            self.verification_timeout_minutes * 60,  # noqa : E501
        )

        # Set a timeout for the token expiration
        token_cache_key = f"verification_token_{email}"
        cache.set(token_cache_key, token, self.token_timeout_minutes * 60)

        return Response(
            {"detail": "Email verification link has been resent" if send_status else "Verification Email could not be sent. Please try again."},
            status=status.HTTP_201_CREATED if send_status else status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


class LoginViewSet(viewsets.ModelViewSet):
    serializer_class = LoginSerializer
    http_method_names = ["post", "head", "options"]  # noqa: E501

    def create(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        access_token = serializer.validated_data["access_token"]
        refresh_token = serializer.validated_data["refresh_token"]
        user = serializer.validated_data["user"]
        return Response(
            {
                "access_token": access_token,
                "refresh_token": refresh_token,
                "user": {
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                    "email": user.email,
                    "phone": user.phone,
                    "role": user.role,
                    "type": user.type,
                },
            },
            status=status.HTTP_200_OK,
        )

  

class TokenRefreshViewSet(viewsets.ModelViewSet):
    serializer_class = CustomTokenRefreshSerializer
    http_method_names = ["post", "head", "options"]  # noqa: E501
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
        except TokenError as e:
            raise InvalidToken(e.args[0])
        return Response(
            serializer.validated_data, status=status.HTTP_201_CREATED
        )


class TechnologyViewSet(viewsets.ModelViewSet):
    pagination_class = None
    queryset = Technology.objects.all().order_by("name")
    serializer_class = TechnologySerializer
    permission_classes = [
        IsAuthenticated,
        IsClientOrCoderPermission,
    ]  # noqa : E501
    http_method_names = ["get", "post", "head", "options"]
    lookup_field = "id"
    filter_backends = (DjangoFilterBackend,)
    filterset_class = filters.TechnologyDropdownFilter

    def perform_create(self, serializer):
        user = self.request.user
        serializer.save(user=user)


class RecommendedTechnologyViewSet(viewsets.ModelViewSet):
    serializer_class = TechnologySerializer
    http_method_names = ["get", "head", "options"]
    lookup_field = "id"

    def get_queryset(self):
        queryset = Technology.objects.filter(is_approved=True)
        if "id" in self.kwargs:
            return queryset
        else:
            return queryset.order_by("?")[:5]


class AddressViewSet(viewsets.ModelViewSet):
    serializer_class = ClientAddressSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ["get", "post", "put", "patch", "head", "options"]
    lookup_field = "id"

    def get_serializer_class(self):
        if getattr(self, 'swagger_fake_view', False):
            return CoderAddressSerializer
        user = self.request.user
        role = user.role
        if role == "CLIENT":
            return ClientAddressSerializer
        elif role == "CODER":
            return CoderAddressSerializer
        else:
            super().get_serializer_class()

    def get_queryset(self):
        return Address.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        user = self.request.user
        serializer.save(user=user)


class CompanyDetailsViewset(viewsets.ModelViewSet):
    serializer_class = CompanyDetailsSerializer
    permission_classes = [
        IsAuthenticated,
        IsClientOrReadOnly,
    ]
    http_method_names = ["get", "post", "put", "patch", "head", "options"]
    lookup_field = "id"

    def get_queryset(self):
        return CompanyDetails.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        user = self.request.user
        serializer.save(user=user)


class PasswordChangeViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = PasswordChangeSerializer
    http_method_names = ["post", "head", "options"]

    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.change_password(request.user)
        return Response({"success": ["Your password has been changed!"]})


class ResetPasswordViewset(viewsets.ModelViewSet):
    serializer_class = PasswordResetSerializer
    http_method_names = ["post", "head", "options"]

    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']
        try:
            user = User.objects.get(email=email)
            current_site = get_current_site(request)
            EmailUtil.send_reset_email(user, current_site)  
        except User.DoesNotExist:
            return Response({"message": "Password reset instructions has been sent Successfully"})
        except Exception as e:
            return Response({
                "message": f"something went wrong. {e}"   
            }, status=status.HTTP_424_FAILED_DEPENDENCY)
        return Response({"message": "Password reset instructions has been sent Successfully"})


class SetNewPasswordViewset(viewsets.ModelViewSet):
    serializer_class = SetNewPasswordSerializer
    http_method_names = ["post", "head", "options"]

    def create(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response({"message": ["Your password has been successfully reset."]})


class SkillViewSet(viewsets.ModelViewSet):
    serializer_class = SkillSerializer
    permission_classes = [IsAuthenticated, IsCoder]
    http_method_names = ["get", "post", "put", "patch", "head", "options"]
    lookup_field = "id"

    def get_queryset(self):
        return Skill.objects.filter(user=self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = self.serializer_class(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(data=serializer.data, status=status.HTTP_201_CREATED)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class CoderSkillsExperienceViewSet(viewsets.ModelViewSet):
    serializer_class = CoderSkillsExperienceSerializer
    permission_classes = [IsAuthenticated, IsCoder]
    http_method_names = ["get", "post", "put", "patch", "head", "options"]
    lookup_field = "id"

    def get_queryset(self):
        return CoderSkillsExperience.objects.filter(user=self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = self.serializer_class(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(data=serializer.data, status=status.HTTP_201_CREATED)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class DigitalPresenceViewSet(viewsets.ModelViewSet):
    permission_classes = [
        IsAuthenticated,
        IsClientOrCoderPermission,
    ]  # noqa : E501
    http_method_names = ["get", "post", "put", "patch", "head", "options"]
    lookup_field = "id"

    def get_serializer_class(self):
        if getattr(self, 'swagger_fake_view', False):
            return CoderDigitalPresenceSerializer
        user = self.request.user
        role = user.role
        if role == "CODER":
            return CoderDigitalPresenceSerializer
        elif role == "CLIENT":
            return ClientDigitalPresenceSerializer
        else:
            super().get_serializer_class()

    def get_queryset(self):
        user = self.request.user
        return DigitalPresence.objects.filter(user=user)

    def create(self, request, *args, **kwargs):
        digital_data = request.data
        serializer = self.get_serializer(data=digital_data)
        serializer.is_valid(raise_exception=True)
        obj = self.get_serializer_class()(self.perform_create(serializer)).data
        try:
            send_status = Util.send_verification_email(user=self.request.user)
        except Exception as e:
            obj["message"] = f"Error occurred while sending verification email. {e}"
            return Response(
                obj,
                status=status.HTTP_424_FAILED_DEPENDENCY,
            )
        if not send_status:
            obj["message"] = "Verification Email could not be sent. Please use resend verification mail to get the mail"
            return Response(
                obj,
                status=status.HTTP_424_FAILED_DEPENDENCY,
            )
        else:
            obj["message"] = "Verification Email Sent"
            return Response(
                obj, status=status.HTTP_201_CREATED
            )
        
    def perform_create(self, serializer):
        user = self.request.user
        return serializer.save(user=user)
        

class CertificationViewSet(viewsets.ModelViewSet):
    serializer_class = CertificationSerializer
    permission_classes = [IsAuthenticated, IsCoder]
    http_method_names = ["get", "post", "put", "patch", "head", "options"]
    lookup_field = "id"

    def get_queryset(self):
        return Certification.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class DegreeViewSet(viewsets.ModelViewSet):
    serializer_class = DegreeSerializer
    permission_classes = [IsAuthenticated, IsCoder]
    http_method_names = ["get", "post", "put", "patch", "head", "options"]
    lookup_field = "id"

    def get_queryset(self):
        return Degree.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class EducationalQualificationViewSet(viewsets.ModelViewSet):
    serializer_class = EducationalQualificationSerializer
    permission_classes = [IsAuthenticated, IsCoder]
    http_method_names = ["get", "post", "put", "patch", "head", "options"]
    lookup_field = "id"

    def get_queryset(self):
        return EducationalQualification.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class UserViewSet(viewsets.ModelViewSet):
    serializer_class = UserSerializer
    http_method_names = ["get", "head", "options"]  # noqa: E501
    permission_classes = [IsEmailVerified]

    def get_queryset(self):
        user = self.request.user
        return User.objects.filter(id=user.id)

    def get_object(self):
        user = self.request.user
        return User.objects.get(id=user.id)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = UserSerializer(instance)
        return Response(serializer.data)


class CoderViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = CoderSerializer
    permission_classes = [IsAuthenticated, IsClientOrCoder]
    http_method_names = ["get", "head", "options"]
    lookup_field = "username"
    filter_backends = [DjangoFilterBackend]
    filterset_class = CoderFilter

    def get_queryset(self):
        user = self.request.user
        if user.role == 'CLIENT':
            return User.objects.filter(role='CODER', is_email_verified=True)
        elif user.role == 'CODER':
            return User.objects.filter(role='CODER', id=user.id, is_email_verified=True)
        
       
class ClientViewSet(viewsets.ModelViewSet):
    serializer_class = ClientSerializer
    http_method_names = ['get', 'head', 'options']
    permission_classes = [IsEmailVerified]
    lookup_field = "username"

    def get_queryset(self):
        user = self.request.user
        if user.role == 'CLIENT':
            return User.objects.filter(role="CLIENT", id = user.id, is_email_verified=True)
        else:
            return User.objects.filter(role="CLIENT", is_email_verified=True)
