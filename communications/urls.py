from django.urls import path
from . import views

urlpatterns = [
    path('send/', views.send_message, name='send-message'),
    path('inbox/', views.inbox, name='inbox'),
    path('message/<int:message_id>/', views.message_detail, name='message-details'),
    path('message/<int:message_id>/reply/', views.reply_message, name='reply-message'),
]