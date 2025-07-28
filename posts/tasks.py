import requests
import logging
from celery import shared_task
from django.utils import timezone
from .models import ScheduledPost

# It's good practice to have a logger for your tasks
logger = logging.getLogger(__name__)

@shared_task
def process_scheduled_posts():
    """
    This task is run by Celery Beat every minute.
    It finds all posts that are due to be published and triggers the
    individual publishing task for each one.
    """
    now = timezone.now()
    due_posts = ScheduledPost.objects.filter(
        scheduled_time__lte=now,
        status='scheduled'
    )

    if due_posts:
        logger.info(f"Found {due_posts.count()} posts to process.")

    for post in due_posts:
        # Mark the post as 'processing' to prevent it from being picked up again
        # in case the worker task takes a moment to start.
        post.status = 'processing'
        post.save()

        # Call the main publishing task asynchronously
        publish_post.delay(post.id)

@shared_task
def publish_post(post_id):
    """
    This task handles the actual posting of a single scheduled post to its
    designated platform (e.g., Facebook).
    """
    try:
        post = ScheduledPost.objects.get(id=post_id)
    except ScheduledPost.DoesNotExist:
        logger.error(f"ScheduledPost with id {post_id} not found. Cannot publish.")
        return

    # --- Facebook Posting Logic ---
    if post.platform == 'facebook':
        # A page must be selected for the post.
        if not post.facebook_page:
            post.status = 'error'
            post.save()
            logger.error(f"Post {post.id} failed: No Facebook Page was selected for this post.")
            return

        page = post.facebook_page
        page_id = page.page_id
        page_access_token = page.access_token # Use the page-specific token

        # The page must have a valid token.
        if not page_access_token:
            post.status = 'error'
            post.save()
            logger.error(f"Post {post.id} failed: The selected page '{page.name}' has no access token.")
            return

        try:
            payload = {
                'message': post.caption,
                'access_token': page_access_token
            }

            # Use different endpoints for posts with images vs. text-only posts
            if post.media_url:
                publish_url = f"https://graph.facebook.com/v19.0/{page_id}/photos"
                payload['url'] = post.media_url
            else:
                publish_url = f"https://graph.facebook.com/v19.0/{page_id}/feed"

            response = requests.post(publish_url, data=payload)
            response_data = response.json()

            # Handle API errors, such as an expired token
            if 'error' in response_data:
                error = response_data['error']
                logger.error(f"Facebook API error for post {post.id}: {error.get('message')}")
                post.status = 'error'
                # If token is invalid, you might want to de-authorize the page here
                if error.get('code') == 190: # Error code 190 is for invalid/expired tokens
                    page.access_token = None
                    page.save()
                    logger.warning(f"Removed expired access token for page '{page.name}'.")

            elif response.status_code == 200 and 'id' in response_data:
                post.status = 'posted'
                # Optionally save the ID of the post on Facebook
                # post.social_media_post_id = response_data['id']
                logger.info(f"Successfully published post {post.id} to Facebook page '{page.name}'.")

            else:
                post.status = 'error'
                logger.error(f"Failed to publish post {post.id}. Unknown error. Response: {response_data}")

            post.save()

        except Exception as e:
            logger.error(f"An unexpected exception occurred while publishing post {post.id}: {str(e)}")
            post.status = 'error'
            post.save()

    # --- Instagram Posting Logic (Placeholder) ---
    elif post.platform == 'instagram':
        # You would add your multi-user Instagram posting logic here
        logger.warning(f"Instagram posting for post {post.id} is not yet implemented.")
        post.status = 'error'
        post.save()

