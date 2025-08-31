from django.contrib import admin
from .models import Meeting, MeetingDetails

@admin.register(Meeting)
class MeetingAdmin(admin.ModelAdmin):
    list_display = ('name', 'attendee', 'created_by', 'duration', 'description', 'date', 'time', 'url')

@admin.register(MeetingDetails)
class MeetingDetailsAdmin(admin.ModelAdmin):
    list_display = ('student', 'professor', 'academic_year', 'semester', 'duration', 'topics')