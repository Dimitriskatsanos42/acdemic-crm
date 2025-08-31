from django.contrib import admin
from .models import User, Student, Professor

@admin.register(User)
class EventAdmin(admin.ModelAdmin):
    list_display = ('email', 'first_name', 'last_name', 'role', 'is_superuser')

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('user', 'enrolled_courses_list')

    def enrolled_courses_list(self, obj):
        return ", ".join([course.name for course in obj.enrolled_courses.all()])
    enrolled_courses_list.short_description = 'Enrolled Courses'

@admin.register(Professor)
class ProfessorAdmin(admin.ModelAdmin):
    list_display = ('user', 'courses_list')

    def courses_list(self, obj):
        return ", ".join([course.name for course in obj.courses.all()])
    courses_list.short_description = 'Assigned Courses'