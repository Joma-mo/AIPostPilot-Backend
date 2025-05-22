from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import UserProfile
from datetime import datetime, timedelta


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(
            user=instance,
            instagram_id='',
            access_token='',
            refresh_token='',
            token_expires_at=datetime.now() + timedelta(days=60),
        )
