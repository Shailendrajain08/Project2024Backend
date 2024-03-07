from django.shortcuts import render
from rest_framework import viewsets, mixins, permissions
from rest_framework.permissions import AllowAny, IsAuthenticated
from home.serializers import (
    RecommendedJobsSerializer,
    TermsAndConditionsSerializer,
    RecommendedCoderSerializer,
)
from core.models import JobPost
from django_filters.rest_framework import DjangoFilterBackend

from accounts.models import User
from django.db.models.functions import Random
from .models import TermsAndConditions
from accounts.permissions import IsAdmin

# Create your views here.


class RecommendedJobsViewset(viewsets.ModelViewSet):
    serializer_class = RecommendedJobsSerializer
    permission_classes = [AllowAny]
    http_method_names = ["get", "head", "options"]
    lookup_field = "id"

    def get_queryset(self):
        queryset = JobPost.objects.filter(status='OPEN')
        if "id" not in self.kwargs:
            queryset = queryset.order_by('?')[:5]
        return queryset


class RecommendedCoderViewSet(viewsets.ModelViewSet):
    queryset = User.objects.filter(role="CODER", is_email_verified=True).order_by(Random())[:5]
    serializer_class = RecommendedCoderSerializer
    permission_classes = [AllowAny]
    http_method_names = ["get", "head", "options"]


class TermsAndConditionsViewSet(viewsets.ModelViewSet):
    queryset = TermsAndConditions.objects.all()
    serializer_class = TermsAndConditionsSerializer
    http_method_names = ["get", "post", "put", "patch", "head", "options"]
    lookup_field = "id"
    
    def get_permissions(self):
        if self.request.method == "GET":
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated(), IsAdmin()]