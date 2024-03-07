# myapp/admin.py
from django.contrib import admin
from .models import CompanyDetails, User, Technology, Address, DigitalPresence, Skill, CoderSkillsExperience, Certification, Degree, EducationalQualification

admin.site.register(User)
admin.site.register(Technology)
admin.site.register(Address)
admin.site.register(CompanyDetails)
admin.site.register(Skill)
admin.site.register(CoderSkillsExperience)
admin.site.register(DigitalPresence)
admin.site.register(Certification)
admin.site.register(Degree)
admin.site.register(EducationalQualification)
