from django.db import models

from accounts.models import Student, Professor

# Create your models here.
class Course(models.Model):
    code = models.CharField(max_length=20, unique=True)
    semester = models.IntegerField()
    semester_label = models.CharField(max_length=20, blank=True)
    name = models.CharField(max_length=255)
    credits = models.IntegerField()

    def __str__(self):
        return self.name

class StudentEnrollment(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    date_enrolled = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('student', 'course')

class ProfessorEnrollment(models.Model):
    professor = models.ForeignKey(Professor, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    date_enrolled = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('professor', 'course')