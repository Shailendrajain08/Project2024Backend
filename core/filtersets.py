import django_filters
from .models import JobPost, JobPostV2, TimeZone, Expertise, Timesheet
from .models import (
    SIZE_OF_PROJECT,
    BUDGET_CHOICES,
    DURATION,
    JOB_STATUS_CHOICES,
    CODER_RESIDE,
    TIMESHEET_STATUS,
    PAYMENT_STATUS
)  # noqa:  E501


class JobPostFilter(django_filters.FilterSet):
    title = django_filters.CharFilter(lookup_expr="icontains")
    description = django_filters.CharFilter(lookup_expr="icontains")
    technologies = django_filters.CharFilter(
        method="filter_technologies", label="technologies (case-insensitive)"
    )
    project_size = django_filters.ChoiceFilter(choices=SIZE_OF_PROJECT)
    budget_type = django_filters.ChoiceFilter(choices=BUDGET_CHOICES)
    expertise = django_filters.ModelMultipleChoiceFilter(
        field_name="expertise__expertise",
        to_field_name="expertise",
        queryset=Expertise.objects.all(),
    )
    duration = django_filters.ChoiceFilter(choices=DURATION)
    timezone = django_filters.ModelMultipleChoiceFilter(
        field_name="timezone__name",
        to_field_name="name",
        queryset=TimeZone.objects.all(),
    )
    status = django_filters.ChoiceFilter(choices=JOB_STATUS_CHOICES)
    maximum_budget = django_filters.NumberFilter(lookup_expr="lte")
    maximum_hourly_rate = django_filters.NumberFilter(lookup_expr="lte")
    minimum_hourly_rate = django_filters.NumberFilter(lookup_expr="gte")
    preferred_coder_residence = django_filters.ChoiceFilter(choices=CODER_RESIDE)

    def filter_technologies(self, queryset, name, value):
        return queryset.filter(technologies__name__iexact=value)

    class Meta:
        model = JobPost
        fields = []
        
            
class JobPostFilterV2(django_filters.FilterSet):
    title = django_filters.CharFilter(lookup_expr="icontains")
    description = django_filters.CharFilter(lookup_expr="icontains")
    technologies = django_filters.CharFilter(
        method="filter_technologies", label="technologies (case-insensitive)"
    )
    project_size = django_filters.ChoiceFilter(choices=SIZE_OF_PROJECT)
    budget_type = django_filters.ChoiceFilter(choices=BUDGET_CHOICES)
    expertise = django_filters.ModelMultipleChoiceFilter(
        field_name="expertise__expertise",
        to_field_name="expertise",
        queryset=Expertise.objects.all(),
    )
    duration = django_filters.ChoiceFilter(choices=DURATION)
    timezone = django_filters.ModelMultipleChoiceFilter(
        field_name="timezone__name",
        to_field_name="name",
        queryset=TimeZone.objects.all(),
    )
    status = django_filters.ChoiceFilter(choices=JOB_STATUS_CHOICES)
    maximum_budget = django_filters.NumberFilter(lookup_expr="lte")
    maximum_hourly_rate = django_filters.NumberFilter(lookup_expr="lte")
    minimum_hourly_rate = django_filters.NumberFilter(lookup_expr="gte")
    preferred_coder_residence = django_filters.ChoiceFilter(choices=CODER_RESIDE)

    def filter_technologies(self, queryset, name, value):
        return queryset.filter(technologies__name__iexact=value)

    class Meta:
        model = JobPostV2
        fields = []


class TimesheetFilter(django_filters.FilterSet):
    job_contract = django_filters.CharFilter(
        method="filter_job_contract", label="job_contract (case-insensitive)"
    )
    date = django_filters.DateFilter(lookup_expr='exact')
    description = django_filters.CharFilter(lookup_expr="icontains")
    start_time = django_filters.TimeFilter(lookup_expr="gte")
    end_time = django_filters.TimeFilter(lookup_expr="lte")
    payment_status = django_filters.ChoiceFilter(choices=PAYMENT_STATUS)
    timesheet_status = django_filters.ChoiceFilter(choices=TIMESHEET_STATUS)

    def filter_job_contract(self, queryset, name, value):
        return queryset.filter(job_contract__name__exact=value)
    
    class Meta:
        model = Timesheet
        fields = []
