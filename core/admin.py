from django.contrib import admin

from .models import (
    JobPost,
    TimeZone,
    Expertise,
    JobInvitation,
    JobPostV2,
    MilestoneV2,
    JobProposalV2,
    JobContract,
    Timesheet
)

# Register your models here.
admin.site.register(JobPost)
admin.site.register(JobPostV2)
admin.site.register(MilestoneV2)
admin.site.register(JobProposalV2)
admin.site.register(TimeZone)
admin.site.register(Expertise)
admin.site.register(JobInvitation)
admin.site.register(JobContract)
admin.site.register(Timesheet)
