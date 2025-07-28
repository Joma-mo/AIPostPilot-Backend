from django.db import models
from django.contrib.auth.models import User


class ScheduledPost(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('scheduled', 'Scheduled'),
        ('posted', 'Posted'),
        ('error', 'Error'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    platform = models.CharField(max_length=32, default='instagram')
    caption = models.TextField()
    media_url = models.URLField()
    scheduled_time = models.DateTimeField()
    status = models.CharField(max_length=32, choices=STATUS_CHOICES, default='scheduled')
    created_at = models.DateTimeField(auto_now_add=True)
    facebook_page = models.ForeignKey('users.FacebookPage', on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.scheduled_time} - {self.status}"
