from django.shortcuts import render, redirect, HttpResponseRedirect
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.db.models import Q

from datetime import datetime, date, timedelta, time

from .forms import MeetingForm, MeetingDetailsForm
from .models import Meeting, MeetingDetails
from . import calendar
from accounts.models import User, Professor
from academic_crm.models import Notification

def _render_calendar(year, month):
    # Default to current year and month if not provided
    today = date.today()
    year = int(year) if year else today.year
    month = int(month) if month else today.month

    # Generate the current calendar
    cal = calendar.BootstrapHTMLCalendar()
    calendar_html = cal.formatmonth(year, month)

    # Calculate previous and next months
    current_date = datetime(year, month, 1)
    prev_date = (current_date - timedelta(days=1)).replace(day=1)
    next_date = (current_date + timedelta(days=31)).replace(day=1)

    return {
        'calendar': calendar_html,
        'current_date': current_date.strftime("%B %Y"),
        'prev_date': prev_date,
        'next_date': next_date
    }    

def _render_events_per_day(request, year, month, day):
    selected_date = datetime(year, month, day).date()

    # Generate 30-minute time slots from 8:00 AM to 6:00 PM
    start_time = time(8, 0)
    end_time = time(18, 0)
    time_slots = []
    current_time = datetime.combine(selected_date, start_time)

    while current_time.time() <= end_time:
        time_slots.append(current_time.time())
        current_time += timedelta(minutes=30)

    # Fetch meetings for the selected date
    meetings = Meeting.objects.filter(date=selected_date)
    
    # Filter meetings: either created by the professor or associated with them
    meetings = meetings.filter(
        Q(created_by=request.user) | Q(attendee=request.user.email)
    )

    meetings_dict = {meeting.time: meeting for meeting in meetings}

    # Add additional context for template rendering
    meetings_data = []
    for meeting_time in time_slots:
        meeting = meetings_dict.get(meeting_time, None)
        meetings_data.append({
            'time': meeting_time,
            'meeting': meeting
        })

    # Handle adding events
    if request.method == 'POST':
        print(request.POST.get('time'))
        form = MeetingForm(request.POST, user=request.user, date=selected_date, time=request.POST.get('time'))
        if form.is_valid():
            new_meeting = form.save()
            # new_meeting = form.save(commit=False)

            """new_meeting.created_by = request.user

            new_meeting.date = selected_date
            new_meeting.time = request.POST.get('time')

            # Handle missing duration
            if not new_meeting.duration:
                new_meeting.duration = None

            new_meeting.save()"""
            
            # Notify the associated user
            try:
                attendee_email = new_meeting.attendee
                attendee = User.objects.get(email=attendee_email)
                Notification.objects.create(
                    user=attendee,
                    meeting=new_meeting,
                    message=f"Ο χρήστης {request.user.get_full_name()} σας προσκάλεσε στη συνάντηση με τίτλο '{new_meeting.name}'"
                )
            except User.DoesNotExist:
                pass  # Handle case where professor email is invalid

            return redirect('events-list-calendar', year=year, month=month, day=day)
    else:
        form = MeetingForm(user=request.user)
        
    return {
        'selected_date': selected_date,
        'time_slots': time_slots,
        'meetings_data': meetings_data,
        'form': form,
        'role': request.user.role,
    }

def mainPage(request, year=None, month=None, day=None):
    calendar_context = _render_calendar(year, month)

    if day != None:
        events_per_day_context = _render_events_per_day(request, year, month, day)

        # Handle redirect
        if isinstance(events_per_day_context, HttpResponseRedirect):
            return events_per_day_context
        
        # Merge contexts for rendering
        context = {**calendar_context, **events_per_day_context}
    else:
        context = calendar_context
    
    return render(request, 'events/main.html', context)

@login_required
def submit_meeting_details(request, meeting_id):
    meeting = get_object_or_404(Meeting, id=meeting_id)
    
    # Ensure only students can access this view
    if request.user.is_student():
        return HttpResponseForbidden("Only professors can submit meeting details.")
    
    professor = request.user
    
    if request.user == meeting.created_by:
        student = User.objects.get(email=meeting.attendee)
    else:
        student = meeting.created_by

    if request.method == 'POST':
        form = MeetingDetailsForm(request.POST, professor=professor, student=student)
        if form.is_valid():
            # Retrieve professor details from the form
            professor_first_name = form.cleaned_data['professor_first_name']
            professor_last_name = form.cleaned_data['professor_last_name']
            
            print(professor_first_name, professor_last_name)

            if not professor:
                form.add_error(None, "Professor not found. Please check the entered first and last name.")
            else:
                # Save the meeting details and associate the professor
                meeting_details = form.save(commit=False)
                
                if request.user == meeting.created_by:
                    meeting_details.professor = request.user
                    meeting_details.student = User.objects.get(email=meeting.attendee)
                else:
                    meeting_details.professor = User.objects.get(email=meeting.attendee)
                    meeting_details.student = meeting.created_by
                meeting_details.save()
                return redirect('current-month-year-calendar')  # Redirect to events main page
    else:
        form = MeetingDetailsForm(professor=professor, student=student)

    return render(request, 'events/submit_meeting_details.html', {'form': form, 'meeting': meeting})

@login_required
def accept_meeting(request, meeting_id):
    meeting = get_object_or_404(Meeting, id=meeting_id)

    """# Ensure the logged-in user is the invited professor
    if meeting.attendee != request.user.email:
        return HttpResponseForbidden("You are not authorized to perform this action.")"""

    # Update the event status
    meeting.status = 'accepted'
    meeting.save()

    # Notify the meeting creator
    creator = meeting.created_by
    Notification.objects.create(
        user=creator,
        meeting=meeting,
        message=f"Ο χρήστης {request.user.get_full_name()} αποδέχτηκε τη συνάντηση με τίτλο '{meeting.name}'."
    )
    
    return redirect('events-list-calendar', year=meeting.date.year, month=meeting.date.month, day=meeting.date.day)

    # return redirect('view-event', meeting_id=meeting.id)

@login_required
def decline_meeting(request, meeting_id):
    meeting = get_object_or_404(Meeting, id=meeting_id)

    """# Ensure the logged-in user is the invited professor
    if meeting.attendee != request.user.email:
        return HttpResponseForbidden("You are not authorized to perform this action.")"""

    # Update the event status
    meeting.status = 'declined'
    meeting.save()
    
    # Notify the meeting creator
    creator = meeting.created_by
    Notification.objects.create(
        user=creator,
        meeting=meeting,
        message=f"Ο χρήστης '{request.user.get_full_name()}' απέρριψε τη συνάντηση με τίτλο '{meeting.name}'."
    )
    
    return redirect('events-list-calendar', year=meeting.date.year, month=meeting.date.month, day=meeting.date.day)

    # return redirect('view-event', meeting_id=event.id)

@login_required
def view_event(request, meeting_id):
    meeting = get_object_or_404(Meeting, id=meeting_id)

    # Render event details
    return render(request, 'events/view_event.html', {'meeting': meeting})

def edit_event(request, meeting_id):
    meeting = get_object_or_404(Meeting, id=meeting_id)
    
    if request.method == 'POST':
        form = MeetingForm(request.POST, user=request.user, instance=meeting)
        
        if form.is_valid():
            form.save()
            
        if request.user != meeting.created_by:
            # Notify the student about the update
            Notification.objects.create(
                user=meeting.created_by,
                meeting=meeting,
                message=f"Η συνάντηση '{meeting.name}' τροποποιήθηκε από τον χρήστη {request.user.get_full_name()}."
            )
        else:
            # Notify the student about the update
            attendee_email = meeting.attendee
            attendee = User.objects.get(email=attendee_email)
            Notification.objects.create(
                user=attendee,
                meeting=meeting,
                message=f"Η συνάντηση '{meeting.name}' τροποποιήθηκε από τον χρήστη {request.user.get_full_name()}."
            )
        
        return redirect('events-list-calendar', year=meeting.date.year, month=meeting.date.month, day=meeting.date.day)
    else:
        form = MeetingForm(user=request.user,instance=meeting)

    return render(request, 'events/edit_event.html', {'form': form, 'event': meeting})

def delete_event(request, meeting_id):
    meeting = get_object_or_404(Meeting, id=meeting_id)

    """if request.user.is_student() and event.professor_name != request.user.email:
        return HttpResponseForbidden("Students can only delete their own events.")"""
    
    if request.user != meeting.created_by:
        # Notify the student about the update
        Notification.objects.create(
            user=meeting.created_by,
            meeting=meeting,
            message=f"Η συνάντηση '{meeting.name}' διαγράφηκε από τον χρήστη {request.user.get_full_name()}."
        )
    else:
        # Notify the student about the update
        attendee_email = meeting.attendee
        attendee = User.objects.get(email=attendee_email)
        Notification.objects.create(
            user=attendee,
            meeting=meeting,
            message=f"Η συνάντηση '{meeting.name}' διαγράφηκε από τον χρήστη {request.user.get_full_name()}."
        )
        
    meeting_date = meeting.date  # Save the event date for redirection
    meeting.delete()
    
    # Redirect to the same day's event list after deletion
    return redirect('events-list-calendar', year=meeting_date.year, month=meeting_date.month, day=meeting_date.day)