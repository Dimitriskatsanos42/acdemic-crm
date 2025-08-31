from django.shortcuts import render, redirect, HttpResponseRedirect
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404

from .models import Notification

@login_required
def mark_notifications_read(request):
    request.user.notifications.update(is_read=True)
    return JsonResponse({'status': 'success'})

@login_required
def view_notification(request, notification_id):
    # Get the notification
    notification = get_object_or_404(Notification, id=notification_id, user=request.user)

    # Mark this specific notification as read
    if not notification.is_read:  # Only update if unread
        notification.is_read = True
        notification.save()

    # Redirect to the associated event if available
    if notification.meeting:
        return redirect('view-event', meeting_id=notification.meeting_id)  # Replace 'view-event' with the actual event view URL name

    # Fallback if no event is associated
    # return redirect('notifications')