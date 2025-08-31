from django.db.models import Avg, Count, Max, Min, Sum
from events.models import Meeting, MeetingDetails
from datetime import datetime

def get_stats(professor):
    # Aggregate statistics
    
    stats = {
        "total_events": Meeting.objects.filter(professor=professor).count(),
        "average_duration": Event.objects.filter(duration__isnull=False).aggregate(Avg('duration'))['duration__avg'],
        "events_per_professor": list(Event.objects.values('professor_name').annotate(total=Count('id')).order_by('-total')),
        "total_duration": Event.objects.filter(duration__isnull=False).aggregate(Sum('duration'))['duration__sum'],
        "durations_per_month": list(
            Event.objects.filter(duration__isnull=False)
            .annotate(month=Count('date__month'))
            .values('date__month')
            .annotate(total=Sum('duration'))
            .order_by('date__month')
        ),
        "max_duration": Event.objects.aggregate(Max('duration'))['duration__max'],
        "min_duration": Event.objects.aggregate(Min('duration'))['duration__min'],
        "temporal_distribution": {
            "days": list(Event.objects.values('date').annotate(total=Count('id')).order_by('-total')),
            "hours": list(Event.objects.values('time').annotate(total=Count('id')).order_by('time')),
        }
    }

    return stats
