from django.db import models
from django.contrib.auth.models import User


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    instagram_id = models.CharField(max_length=255)
    access_token = models.TextField()
    refresh_token = models.TextField(blank=True, null=True)
    token_expires_at = models.DateTimeField()


    facebook_access_token = models.CharField(max_length=512, blank=True, null=True)
    facebook_token_expires_at = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f"{self.user.username}'s Instagram"


class FacebookPage(models.Model):
    user_profile = models.ForeignKey('UserProfile', on_delete=models.CASCADE, related_name='facebook_pages')
    page_id = models.CharField(max_length=100, unique=True)
    name = models.CharField(max_length=255)
    access_token = models.CharField(max_length=512)

    def __str__(self):
        return self.name
