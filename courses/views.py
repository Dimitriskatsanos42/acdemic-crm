from django.shortcuts import render
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from courses.models import Course, StudentEnrollment, ProfessorEnrollment
from django.contrib import messages

from datetime import date

@login_required
def dashboard(request):
    def get_current_semester():
        """Determine the current semester based on today's date."""
        today = date.today()
        if today.month in [10, 11, 12, 1]:  # October to January
            return "winter"
        elif today.month in [2, 3, 4, 5, 6]:  # February to June
            return "spring"
        return None
    
    current_semester = get_current_semester()
    
    if request.user.role == "student":
        student = request.user.student_profile
        # Fetch all courses or filter based on search query
        query = request.GET.get('q', '')  # Get the search query from URL
        
        # Available courses (not yet enrolled and matching current semester)
        available_courses = Course.objects.filter(
            semester_label=current_semester,
            name__icontains=query
        ).exclude(
            studentenrollment__student=student
        )
        
        # Fetch the student's enrolled courses
        enrolled_courses = student.enrolled_courses.all()
        return render(request, 'courses/student_dashboard.html', {
            'available_courses': available_courses,
            'enrolled_courses': enrolled_courses,
            'query': query,  # Pass the query back to the template
            'current_semester': current_semester
        })
        
    else:
        professor = request.user.professor_profile
                
        # Courses headed by the professor
        assigned_courses = professor.assigned_courses.all()

        # Courses without a head and in the current semester
        available_courses = Course.objects.filter(
            semester_label=current_semester
        ).exclude(
            professorenrollment__professor=professor
        )

        return render(request, 'courses/professor_dashboard.html', {
            'assigned_courses': assigned_courses,
            'available_courses': available_courses,
        })

@login_required
def enroll(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    
    if request.user.role == "student":
        student = request.user.student_profile
        
        # Check if the student has reached the maximum enrollment limit
        if StudentEnrollment.objects.filter(student=student).count() >= 8:
            messages.error(request, "Δεν μπορείτε να εγγραφείτε σε πάνω από οκτώ (8) μαθήματα!")
            return redirect('dashboard')  # Redirect if limit reached
        
        StudentEnrollment.objects.get_or_create(student=student, course=course)
    else:
        professor = request.user.professor_profile

        # Check if the professor is already heading the course
        if professor.assigned_courses.filter(id=course.id).exists():
            return redirect('dashboard')

        # Associate the professor with the course
        ProfessorEnrollment.objects.get_or_create(professor=professor, course=course)
        
    return redirect('dashboard')

@login_required
def unenroll(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    
    if request.user.role == "student":
        student = request.user.student_profile
        StudentEnrollment.objects.filter(student=student, course=course).delete()
    else:
        professor = request.user.professor_profile

        # Check if the professor is the head of the course
        if not professor.assigned_courses.filter(id=course.id).exists():
            return redirect('dashboard')
        
        # Remove the professor from the course
        ProfessorEnrollment.objects.filter(professor=professor, course=course).delete()
        
    return redirect('dashboard')

@login_required
def enrolled_students(request, course_id):
    course = get_object_or_404(Course, id=course_id)

    # Check if the professor is heading the course
    if request.user.role == "professor":
        professor = request.user.professor_profile
        
        if professor.assigned_courses.filter(id=course.id).exists():
            enrolled_students = StudentEnrollment.objects.filter(course=course)
            return render(request, 'courses/enrolled_students.html', {
                'course': course,
                'enrolled_students': enrolled_students,
            })

    return redirect('dashboard')