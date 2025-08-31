from django.db import models
from datetime import time
# from django.contrib.auth import get_user_model

from accounts.models import User, Professor, Student

# User = get_user_model()

class Meeting(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('declined', 'Declined'),
    ]
    
    DURATION_CHOICES = [
        (30, "30'"),
        (45, "45'"),
        (60, "60'"),
        (75, "75'"),
        (90, "90'"),
    ]

    name = models.CharField('Meeting Title', max_length=120)
    attendee = models.CharField('Attendee Name', max_length=120)
    url = models.CharField('Meeting URL', blank=True, null=True, max_length=120)
    date = models.DateField('Meeting Date')
    time = models.TimeField('Meeting Start Time', default=time(12, 0))
    description = models.TextField(blank=True)
    duration = models.PositiveIntegerField(choices=DURATION_CHOICES, null=True, blank=True, default=30)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='pending',
    )
    
    # Method to get the label of the attendee value
    def get_attendee_full_name(self):
        try:
            # Fetch the professor object corresponding to the email stored in professor_name
            attendee_user = User.objects.get(email=self.attendee)
            return attendee_user.get_full_name()  # Return the full name as the label
        except Student.DoesNotExist:
            return self.created_by  # Return the email if no matching professor is found

    def __str__(self):
        return f"{self.name}"
    
class MeetingDetails(models.Model):
    TOPICS_CHOICES = [
        ('attendance', 'Παρουσία σε παραδόσεις'),
        ('understanding', 'Κατανόηση ύλης'),
        ('difficulties', 'Μαθησιακές δυσκολίες'),
        ('notes', 'Σημειώσεις, τρόπος μελέτης'),
        ('assignments', 'Ασκήσεις, βιβλιογραφία, διαδικασία δηλώσεων'),
        ('projects', 'Ομαδικές/Ατομικές εργασίες'),
        ('labs', 'Εργαστήρια'),
        ('diploma', 'Επιλογή διπλωματικής εργασίας'),
        ('exams', 'Εξεταστικές περίοδοι'),
        ('erasmus', 'Συμμετοχή σε Erasmus (σπουδές)'),
        ('digital_skills', 'Ψηφιακές δεξιότητες'),
        ('languages', 'Ξένες γλώσσες'),
        ('seminars', 'Σεμινάρια/Συνέδρια'),
        ('graduation', 'Ορκωμοσία'),
        ('career', 'Επαγγελματικές προοπτικές'),
        ('faculty_issues', 'Θέματα με διδάσκοντες'),
        ('secretariat', 'Θέματα με τη γραμματεία'),
        ('personal', 'Προσωπικά θέματα'),
    ]

    # Fields
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='meeting_details')
    professor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='meetings_with_students')
    academic_year = models.CharField(max_length=9)
    semester = models.CharField(max_length=20)
    duration = models.CharField(max_length=5)
    topics = models.JSONField()  # Store multiple selected topics as a JSON list
    comments = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"MeetingDetails(student={self.student}, professor={self.professor})"