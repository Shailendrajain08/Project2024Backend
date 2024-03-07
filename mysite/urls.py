"""
URL configuration for mysite project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from accounts.views import (
    TechnologyViewSet,
    LoginViewSet,
    RegisterViewSet,
    VerifyEmailViewSet,
    AgencyViewSet,
    RecommendedTechnologyViewSet,
    AddressViewSet,
    ResendEmailVerificationViewSet,
    CompanyDetailsViewset,
    ResetPasswordViewset,
    SetNewPasswordViewset,
    PasswordChangeViewSet,
    SkillViewSet,
    CoderSkillsExperienceViewSet,
    DigitalPresenceViewSet,
    CertificationViewSet,
    DegreeViewSet,
    EducationalQualificationViewSet,
    UserViewSet,
    CoderViewSet,
    TokenRefreshViewSet,
    ClientViewSet
) # noqa: E501

from admin_app.views import AdminDashboardViewSet, AdminLoginViewSet
from home.views import TermsAndConditionsViewSet
from core.views import TimeZoneViewSet, MilestoneV2Viewset, ProposalV2Viewset, TimesheetViewSet
from home.views import RecommendedCoderViewSet

from rest_framework.routers import DefaultRouter
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

from core.views import JobPostViewset, JobInvitationViewSet, JobPostV2Viewset, ContractViewSet
from home.views import RecommendedJobsViewset


router = DefaultRouter()
router_v2 = DefaultRouter()
router.register("register", RegisterViewSet)
router.register("agency", AgencyViewSet, basename="agency")
router.register("register", RegisterViewSet, basename="register")
router.register("login", LoginViewSet, basename="login")  # noqa : E501
router.register("admin-dashboard", AdminDashboardViewSet, basename="dashboard")
router.register("token-refresh", TokenRefreshViewSet, basename="token-refresh")  # noqa : E501
router.register("admin-login", AdminLoginViewSet, basename="admin-login")

router.register(
    "technology-dropdown", TechnologyViewSet, basename="technology"
)  # noqa: E501
router.register("company-details", CompanyDetailsViewset, basename="company")
router.register(
    "recommended-technology",
    RecommendedTechnologyViewSet,
    basename="recommended-technology",
)
router.register(
    "verify-email", VerifyEmailViewSet, basename="verify-email"
)  # noqa: E501
router.register("address", AddressViewSet, basename="address")  # noqa : E501
router.register(
    "resend-verification-email",
    ResendEmailVerificationViewSet,
    basename="resend-verification-email",
)  # noqa : E501
router.register("skills", SkillViewSet, basename="skills")
router.register("skills-experience", CoderSkillsExperienceViewSet, basename="skills-experience")
router.register("coder", CoderViewSet, basename="coder")
router.register("change-password", PasswordChangeViewSet, basename="change-password")
router.register("password-reset", ResetPasswordViewset, basename="password-reset")
router.register("password-reset-confirm", SetNewPasswordViewset, basename="password-reset-confirm", )
router.register("timezone", TimeZoneViewSet, basename="timezone")
router.register(
    "digital-presence", DigitalPresenceViewSet, basename="digital-presence"
)  # noqa:  E501
router.register("job-posts", JobPostViewset, basename="job-posts")
router_v2.register("job-posts", JobPostV2Viewset, basename="job-posts-v2")
router_v2.register("milestone", MilestoneV2Viewset, basename="milestone-v2")
router_v2.register("proposal", ProposalV2Viewset, basename="proposal-v2")
router.register("recommended-jobs", RecommendedJobsViewset, basename="recommended-jobs")
router.register("invited-jobs", JobInvitationViewSet, basename="invited-jobs")
router.register("certification", CertificationViewSet, basename="certification")
router.register("degree", DegreeViewSet, basename="degree")
router.register("educational-qualification", EducationalQualificationViewSet, basename="educationalqualification")
router.register("user", UserViewSet, basename="user")
router.register("recommended-coder", RecommendedCoderViewSet, basename='recommended-coder')
router.register("terms-and-condition", TermsAndConditionsViewSet, basename='terms-and-condition')
router.register("client", ClientViewSet, basename="client")
router_v2.register("contract", ContractViewSet, basename="contract")
router_v2.register("timesheet", TimesheetViewSet, basename='timesheet')

schema_view = get_schema_view(
    openapi.Info(
        title="This is the new Repo for the restructured API's",
        default_version="v2",
        description="This repo is under development.",
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)
urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/v1/", include(router.urls), name='v1'),
    path("api/v2/", include(router_v2.urls), name='v2'),
    path(
        "",
        schema_view.with_ui("swagger", cache_timeout=0),
        name="schema-swagger-ui",
    ),
]  # noqa: E501

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL, document_root=settings.MEDIA_ROOT
    )  # noqa: E501
