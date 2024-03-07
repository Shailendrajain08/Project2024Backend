"""
Views for Core Application
"""
# System level imports
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.db.utils import IntegrityError

# Application level imports

from core.models import TimeZone, JobPost, JobInvitation, JobPostV2
from core.models import TimeZone, JobPost, JobPostV2, JobInvitation,MilestoneV2, JobProposalV2, JobContract, Timesheet


from core.filtersets import JobPostFilter, JobPostFilterV2, TimesheetFilter
from .serializers import (
    JobPostSerializer,
    TimeZoneSerializer,
    JobInvitationSerializer,
    JobInvitationPatchSerializer,
    JobPostV2Serializer, JobPostV2UpdateSerializer, MilestoneV2Serializer,
    ProposalV2Serializer, MilestoneV2UpdateClientSerializer, MilestoneV2UpdateCoderSerializer,
    ProposalV2UpdateCoderSerializer, ProposalV2UpdateClientSerializer, JobContractSerializer,
    TimesheetCoderSerializer, TimesheetClientSerializer
)

from core.permissions import (
    IsClientOrReadOnly,
    IsAuthenticatedAndEmailVerified,
    HasJobInvitationEditPermission,
    IsAdminOrReadOnly, CustomMilestonePermission, CustomProposalPermission, 
    HasTimesheetGetUpdatePermission
)


from accounts.permissions import (
    IsClientOrCoderPermission
)


class JobPostViewset(viewsets.ModelViewSet):
    serializer_class = JobPostSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = JobPostFilter
    permission_classes = [IsAuthenticatedAndEmailVerified, IsClientOrReadOnly]
    http_method_names = ["get", "post", "patch", "head", "options"]
    lookup_field = "id"

    def get_queryset(self):
        user = self.request.user
        if user.role == "CLIENT":
            return JobPost.objects.filter(user=user)
        elif user.role == "CODER":
            return JobPost.objects.all()
        return JobPost.objects.none()

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers
        )


# Create your views here.
class TimeZoneViewSet(viewsets.ModelViewSet):
    pagination_class = None
    queryset = TimeZone.objects.all()
    lookup_field = "id"
    serializer_class = TimeZoneSerializer
    permission_classes = [IsAuthenticated, IsAdminOrReadOnly, IsAuthenticatedAndEmailVerified]
    http_method_names = ["get", "post", "head", "options"]


class JobInvitationViewSet(viewsets.ModelViewSet):
    http_method_names = ["get", "post", "patch", "head", "options"]
    permission_classes = [IsAuthenticated, IsClientOrCoderPermission, HasJobInvitationEditPermission]
    lookup_field = "id"

    def get_queryset(self):
        user = self.request.user
        if user.role == "CLIENT":
            return JobInvitation.objects.filter(client=user)
        elif user.role == "CODER":
            return JobInvitation.objects.filter(coder=user)
        return JobInvitation.objects.none()

    def get_serializer_class(self):
        if self.request.method == "PATCH":
            return JobInvitationPatchSerializer
        else:
            return JobInvitationSerializer

    def perform_create(self, serializer):
        serializer.save(client=self.request.user, status='SENT')

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = self.request.user
        if len(JobPost.objects.filter(user=user, id = request.data['jobpost'])) == 0:
            return Response(
            {"error":"Client can only invite from his jobpost"}, status=status.HTTP_400_BAD_REQUEST
            )
        try:
            self.perform_create(serializer)
        except IntegrityError as e:
            return Response(
            {"error":"Coder is already invited"}, status=status.HTTP_409_CONFLICT
            )
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers
        )
    
    def partial_update(self, request, *args, **kwargs):
        user = self.request.user
        instance = self.get_object()
        kwargs['partial'] = True
        if user.role == "CODER" and len(JobInvitation.objects.filter(coder = user, pk_id = instance.pk_id)):
            if request.data.get("status") and request.data["status"] != "READ" and request.data["status"] != "INVITATION_REJECTED":
                return Response(
                    {"error": "Coder is not allowed to update this status"}, status=status.HTTP_403_FORBIDDEN
                )
        else:
            return Response(
                    {"error": "This status update is not allowed"}, status=status.HTTP_403_FORBIDDEN
                )
        return self.update(request, *args, **kwargs)    


class JobPostV2Viewset(viewsets.ModelViewSet):
    serializer_class = JobPostV2Serializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = JobPostFilterV2
    permission_classes = [IsAuthenticatedAndEmailVerified, IsClientOrReadOnly]
    http_method_names = ["get", "post", "patch", "put", "head", "options"]
    lookup_field = "id"

    def get_queryset(self):
        user = self.request.user
        if user.role == "CLIENT":
            return JobPostV2.objects.filter(user=user)
        elif user.role == "CODER":
            return JobPostV2.objects.all()
        return JobPostV2.objects.none()

    def get_serializer_class(self):
        """allocates different serializers for Create and update."""
        if self.request.method == "POST":
            return JobPostV2Serializer
        elif self.request.method in ["PUT", "PATCH"]:
            return JobPostV2UpdateSerializer
        else:
            return super(JobPostV2Viewset, self).get_serializer_class()

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class MilestoneV2Viewset(viewsets.ModelViewSet):
    serializer_class = MilestoneV2Serializer
    # filter_backends = [DjangoFilterBackend]
    # filterset_class = JobPostFilterV2
    permission_classes = [IsAuthenticatedAndEmailVerified, CustomMilestonePermission]
    http_method_names = ["get", "post", "patch", "put", "head", "options"]
    lookup_field = "id"

    def get_queryset(self):
        user = self.request.user
        if user.role == "CLIENT":
            return MilestoneV2.objects.filter(job_post__user=user)
        elif user.role == "CODER":
            return MilestoneV2.objects.filter(user=user)
        return MilestoneV2.objects.none()

    def get_serializer_class(self):
        """allocates different serializers for Create and update."""
        if getattr(self, 'swagger_fake_view', False):
            return MilestoneV2Serializer
        if self.request.method == "POST":
            return MilestoneV2Serializer
        elif self.request.method in ["PUT", "PATCH"] and self.request.user.role == "CODER":
            return MilestoneV2UpdateCoderSerializer
        elif self.request.method in ["PUT", "PATCH"] and self.request.user.role == "CLIENT":
            return MilestoneV2UpdateClientSerializer
        else:
            return super(MilestoneV2Viewset, self).get_serializer_class()


class ProposalV2Viewset(viewsets.ModelViewSet):
    serializer_class = ProposalV2Serializer
    # filter_backends = [DjangoFilterBackend]
    # filterset_class = JobPostFilterV2
    permission_classes = [IsAuthenticatedAndEmailVerified, CustomProposalPermission]
    http_method_names = ["get", "post", "patch", "put", "head", "options"]
    lookup_field = "id"

    def get_queryset(self):
        user = self.request.user
        if user.role == "CODER":
            return JobProposalV2.objects.filter(user=user)
        elif user.role == "CLIENT":
            return JobProposalV2.objects.filter(job_post__user=user)
        return JobProposalV2.objects.none()

    def get_serializer_class(self):
        """allocates different serializers for Create and update."""
        if getattr(self, 'swagger_fake_view', False):
            return ProposalV2Serializer
        if self.request.method == "POST":
            return ProposalV2Serializer
        elif self.request.method in ["PUT", "PATCH"] and self.request.user.role == "CODER":
            return ProposalV2UpdateCoderSerializer
        elif self.request.method in ["PUT", "PATCH"] and self.request.user.role == "CLIENT":
            return ProposalV2UpdateClientSerializer
        else:
            return super(ProposalV2Viewset, self).get_serializer_class()

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class ContractViewSet(viewsets.ModelViewSet):
    serializer_class = JobContractSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ["get", "head", "options"]
    lookup_field = "id"

    def get_queryset(self):
        user = self.request.user
        if user.role == "CLIENT":
            return JobContract.objects.filter(client_id=user)
        elif user.role == "CODER":
            return JobContract.objects.filter(coder_id=user)
        else:
            return JobContract.objects.none()

class TimesheetViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, HasTimesheetGetUpdatePermission]
    filter_backends = [DjangoFilterBackend]
    filterset_class = TimesheetFilter
    lookup_field = 'id'

    def get_queryset(self):
        user = self.request.user
        if user.role == 'CLIENT':
            return Timesheet.objects.filter(job_contract__job_proposal__job_post__user_id=user.id)
        elif user.role == 'CODER':
            return Timesheet.objects.filter(user=user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers
        )


        
    def get_serializer_class(self):
        if getattr(self, 'swagger_fake_view', False):
            return TimesheetClientSerializer
        user = self.request.user
        if user.role == 'CLIENT':
            return TimesheetClientSerializer
        elif user.role == 'CODER':
            return TimesheetCoderSerializer
        