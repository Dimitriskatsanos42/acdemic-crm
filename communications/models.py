from django.db import models
from django.utils.timezone import now
from accounts.models import User

class Message(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages')
    content = models.TextField()
    timestamp = models.DateTimeField(default=now)
    is_read = models.BooleanField(default=False)
    reply_to = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name='replies')

    def __str__(self):
        content_snippet = (self.content[:30] + '...') if len(self.content) > 30 else self.content
        return f"From {self.sender.email} to {self.receiver.email} at {self.timestamp.strftime('%Y-%m-%d %H:%M:%S')}: {content_snippet}"