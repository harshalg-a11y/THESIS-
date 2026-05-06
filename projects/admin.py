from django.contrib import admin
from .models import ThesisRequest, Milestone, Attachment

admin.site.register(ThesisRequest)
admin.site.register(Milestone)
admin.site.register(Attachment)
