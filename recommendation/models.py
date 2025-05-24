from django.db import models
from django.contrib.auth.models import User

class EngagementLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post_time = models.DateTimeField()
    likes = models.IntegerField(default=0)
    comments = models.IntegerField(default=0)
    reach = models.IntegerField(default=0)  # Optional
    created_at = models.DateTimeField(auto_now_add=True)

