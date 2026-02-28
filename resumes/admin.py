from django.contrib import admin
from .models import Resume, Skill, Education, Experience, Certification, Project

admin.site.register(Resume)
admin.site.register(Skill)
admin.site.register(Education)
admin.site.register(Experience)
admin.site.register(Certification)
admin.site.register(Project)