from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.db.models.functions import ExtractMonth
from events.models import MeetingDetails
from django.db.models import Count, Avg, Max, Min, Sum, Q
from datetime import datetime, time, timedelta
from collections import defaultdict

from events.models import Meeting, MeetingDetails

def prepare_data_for_display(data, keyword):
    return [{keyword: key, "total": value} for key, value in data.items()]

@login_required
def stats_view(request):
    # Get meeting details forms submitted by the current professor
    meetings = MeetingDetails.objects.filter(professor=request.user)
    
    # Filter meetings from events page by the current professor
    filtered_meetings = Meeting.objects.filter(
        Q(created_by=request.user) | Q(attendee=request.user.email)
    )
    
    init_num_meetings = 4
    
    # Text-based statistics
    num_meetings = len(filtered_meetings) + init_num_meetings
    avg_duration = meetings.aggregate(avg_duration=Avg('duration'))['avg_duration']
    total_duration = meetings.aggregate(total_duration=Sum('duration'))['total_duration']
    max_duration = meetings.aggregate(max_duration=Max('duration'))['max_duration']
    min_duration = meetings.aggregate(min_duration=Min('duration'))['min_duration']
    
    # Chart-based statistics
    meetings_per_date = list(filtered_meetings.values('date').annotate(total=Count('id')).order_by('-total'))
    meetings_per_time = list(filtered_meetings.values('time').annotate(total=Count('id')).order_by('time')),
    
    # Define the start and end times
    start_time = datetime.strptime("08:00", "%H:%M")
    end_time = datetime.strptime("18:00", "%H:%M")

    # Generate the time objects at 30-minute intervals
    time_slots = []
    current_time = start_time

    while current_time <= end_time:
        time_slots.append(current_time.time())  # Extract the time part
        current_time += timedelta(minutes=30)
        
    days_mapping = {
        "Monday": "Δευτέρα",
        "Tuesday": "Τρίτη",
        "Wednesday": "Τετάρτη",
        "Thursday": "Πέμπτη",
        "Friday": "Παρασκευή",
    }
    
    # Mapping weekday numbers to day names
    days_of_week = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
    
    # Initialize a dictionary to aggregate totals
    meetings_per_day = {day: 0 for day in days_mapping.values()}
    meetings_per_hour = {hour: 0 for hour in time_slots}
    
    # Calculate totals per day of the week
    for entry in meetings_per_time[0]:
        time_obj = entry["time"]

        # Add the total
        meetings_per_hour[time_obj] += entry["total"]
    
    hours_distribution = prepare_data_for_display(meetings_per_hour, "hour")
    
    # Calculate totals per day of the week
    for entry in meetings_per_date:
        # Parse the date
        date_obj = entry["date"]
        # Get the day of the week (0 = Monday, 6 = Sunday)
        day_name = days_of_week[date_obj.weekday()]
        # Add the total to the corresponding day
        meetings_per_day[days_mapping[day_name]] += entry["total"]
    
    days_distribution = prepare_data_for_display(meetings_per_day, "day")
    
    # Predefined majority days and times
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
    
    # Count meetings per topic
    topics_data = {topic[1]: 0 for topic in TOPICS_CHOICES}
    for meeting in meetings:
        for topic in meeting.topics:
            for choice in TOPICS_CHOICES:
                if topic == choice[0]:  # Match topic key
                    topics_data[choice[1]] += 1  # Increment count for topic name

    # Convert data for Chart.js
    topics_distribution = prepare_data_for_display(topics_data, "topic")
    
    distributions = {
        "days": days_distribution,
        "hours": hours_distribution,
        "topics": topics_distribution
    }    
    
    # Context for template
    context = {
        'num_meetings': num_meetings,
        'avg_duration': avg_duration,
        'total_duration': total_duration,
        'max_duration': max_duration,
        'min_duration': min_duration,
        'distributions': distributions,
    }
    
    return render(request, 'stats/stats.html', context)