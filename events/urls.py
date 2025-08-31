from django.urls import path
from . import views

urlpatterns = [
    path('calendar/', views.mainPage, name='current-month-year-calendar'),
    path('calendar/<int:year>/<int:month>/', views.mainPage, name='specified-month-year-calendar'), 
    path('calendar/<int:year>/<int:month>/<int:day>/', views.mainPage, name='events-list-calendar'),
    path('event/edit/<int:meeting_id>/', views.edit_event, name='edit-event'),
    path('event/delete/<int:meeting_id>/', views.delete_event, name='delete-event'),
    path('event/<int:meeting_id>/', views.view_event, name='view-event'),
    path('meeting-details/<int:meeting_id>/', views.submit_meeting_details, name='submit-meeting-details'),
    path('events/<int:meeting_id>/accept/', views.accept_meeting, name='accept-meeting'),
    path('events/<int:meeting_id>/decline/', views.decline_meeting, name='decline-meeting'),
]