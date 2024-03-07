from django_filters import rest_framework as filters
from . import models
from .models import User


class TechnologyDropdownFilter(filters.FilterSet):
    name = filters.CharFilter(field_name="name", lookup_expr="icontains")

    class Meta:
        model = models.Technology
        fields = ("name",)


class CoderFilter(filters.FilterSet):
    technology = filters.CharFilter(field_name='skills_of_user__technology__name', lookup_expr='iexact')
    skill_type = filters.CharFilter(field_name='skills_of_user__skill_type', lookup_expr='icontains')
    expertise_level = filters.CharFilter(field_name='skills_of_user__expertise_level', lookup_expr='icontains')
    hourly_rate__lt = filters.NumberFilter(field_name='coderskillsexperience__hourly_rate', lookup_expr='lt')  
    hourly_rate__gt = filters.NumberFilter(field_name='coderskillsexperience__hourly_rate', lookup_expr='gt')  
    hourly_rate = filters.RangeFilter(field_name='coderskillsexperience__hourly_rate') 
    country = filters.CharFilter(field_name='address__country', lookup_expr='icontains')

    class Meta:
        model = User
        fields = ['technology', 'skill_type', 'hourly_rate__lt', 'hourly_rate__gt', 'hourly_rate', 'country', 
                  'expertise_level']


  