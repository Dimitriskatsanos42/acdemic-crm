from django.contrib import admin
from .models import Course, StudentEnrollment, ProfessorEnrollment

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('code', 'semester', 'semester_label', 'name', 'credits')
    search_fields = ('code', 'semester', 'semester_label', 'name', 'credits')

@admin.register(StudentEnrollment)
class StudentEnrollmentAdmin(admin.ModelAdmin):
    list_display = ('student', 'course', 'date_enrolled')
    search_fields = ('student__user__email', 'course__name', 'course__code')
    # list_filter = ('date_enrolled', 'course__semester')

    def date_enrolled(self, obj):
        return obj.date_enrolled  # Display the enrollment date

@admin.register(ProfessorEnrollment)
class ProfessorEnrollmentAdmin(admin.ModelAdmin):
    list_display = ('professor', 'course', 'date_enrolled')
    search_fields = ('professor__user__email', 'course__name', 'course__code')
    # list_filter = ('date_enrolled', 'course__semester')

    def date_enrolled(self, obj):
        return obj.date_enrolled  # Display the enrollment date