from celery import shared_task
import requests
from .models import ScheduledPost
from django.utils import timezone


@shared_task
def publish_due_posts():
    now = timezone.now()
    due_posts = ScheduledPost.objects.filter(scheduled_time__lte=now, status='scheduled')

    for post in due_posts:
        profile = post.user.userprofile
        access_token = profile.access_token
        ig_user_id = profile.instagram_id

        if not access_token or not ig_user_id:
            post.status = 'error'
            post.save()
            continue

        # Simulate posting (real posting needs Facebook Page and IG Business Account)
        publish_url = f"https://graph.facebook.com/v19.0/{ig_user_id}/media"
        create_payload = {
            'caption': post.caption,
            'image_url': post.media_url,
            'access_token': access_token
        }

        # Step 1: Create media container
        res1 = requests.post(publish_url, data=create_payload)
        media = res1.json()
        if 'id' not in media:
            post.status = 'error'
            post.save()
            continue

        creation_id = media['id']

        # Step 2: Publish media
        publish_url = f"https://graph.facebook.com/v19.0/{ig_user_id}/media_publish"
        res2 = requests.post(publish_url, data={
            'creation_id': creation_id,
            'access_token': access_token
        })

        if res2.status_code == 200:
            post.status = 'posted'
        else:
            post.status = 'error'

        post.save()

    return f"{due_posts.count()} posts processed"
