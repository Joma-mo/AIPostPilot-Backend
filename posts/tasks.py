from celery import shared_task
from django.utils import timezone
from .models import ScheduledPost


@shared_task
def publish_due_posts():
    now = timezone.now()
    due_posts = ScheduledPost.objects.filter(
        scheduled_time__lte=now,
        status='scheduled'
    )

    for post in due_posts:
        # 🚨 Here you’d actually call Instagram API to publish
        post.status = 'posted'  # or 'error' if API fails
        post.save()

    return f"{due_posts.count()} posts published"
