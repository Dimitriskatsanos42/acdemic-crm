import re
from django.db import models
from django.core.exceptions import ValidationError
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import BaseUserManager

class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        """
        Create and return a regular user with the given email and password.
        """
        if not email:
            raise ValueError("The Email field must be set.")
        
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, email, password=None, **extra_fields):
        """
        Create and return a superuser with the given email and password.
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if not extra_fields.get('is_staff'):
            raise ValueError("Superuser must have is_staff=True.")
        if not extra_fields.get('is_superuser'):
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(email, password, **extra_fields)

class User(AbstractUser):
    STUDENT = 'student'
    PROFESSOR = 'professor'

    ROLE_CHOICES = [
        (STUDENT, 'Student'),
        (PROFESSOR, 'Professor'),
    ]

    # Remove the username field
    username = None

    email = models.EmailField(unique=True)

    # Specify the additional attributes
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='professor')

    # Use email as the unique identifier for authentication
    USERNAME_FIELD = 'email'

    # Required fields when creating a superuser
    REQUIRED_FIELDS = ['first_name', 'last_name']

    # Enforce first_name and last_name attributes to be required
    first_name = models.CharField(max_length=150, blank=False, null=False)
    last_name = models.CharField(max_length=150, blank=False, null=False)

    # Link the custom manager
    objects = UserManager()

    def is_student(self):
        return self.role == self.STUDENT

    def is_professor(self):
        return self.role == self.PROFESSOR

    def clean(self):
        super().clean()

        # Ensure email ends with '@uoi.gr'
        if not self.email.endswith('@uoi.gr'):
            raise ValidationError({'email': "All emails must end with '@uoi.gr'."})

        # Additional validation for students
        if self.role == 'student':
            pattern = r'^int\d{5}@uoi\.gr$'
            if not re.match(pattern, self.email):
                raise ValidationError({
                    'email': "Students' emails must start with 'int', followed by 5 digits, and end with '@uoi.gr'."
                })

        # Additional validation for professors
        elif self.role == 'professor':
            pattern = r'^[a-zA-Z]+@uoi\.gr$'
            if not re.match(pattern, self.email):
                raise ValidationError({
                    'email': "Professors' emails must not contain numbers and must end with '@uoi.gr'."
                })

    def __str__(self):
        return self.email

class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='student_profile')
    enrolled_courses = models.ManyToManyField('courses.Course', through='courses.StudentEnrollment')

    def __str__(self):
        return self.user.__str__()

class Professor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='professor_profile')
    assigned_courses = models.ManyToManyField('courses.Course', through='courses.ProfessorEnrollment')

    def __str__(self):
        return self.user.__str__()