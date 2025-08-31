from django.urls import path
from . import views

urlpatterns = [
    path('dashboard', views.dashboard, name='dashboard'),
    path('enroll/<int:course_id>/', views.enroll, name='enroll'),
    path('unenroll/<int:course_id>/', views.unenroll, name='unenroll'),
    path('professor/courses/<int:course_id>/', views.enrolled_students, name='enrolled_students'),
]