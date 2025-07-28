import requests # <-- THIS LINE WAS MISSING
from django.conf import settings
from django.shortcuts import redirect
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from users.models import UserProfile, FacebookPage # Import the new FacebookPage model
from django.utils import timezone
from datetime import timedelta
from .serializers import FacebookPageSerializer # We will create this serializer next

class FacebookLoginView(APIView):
    """
    Redirects the user to Facebook to start the authentication process.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        redirect_uri = settings.FACEBOOK_REDIRECT_URI
        # We need to ask for specific permissions to get the list of pages and their tokens
        scope = [
            'public_profile',
            'pages_show_list',
            'pages_read_engagement',
            'pages_manage_posts',
        ]
        url = (
            f"https://www.facebook.com/v19.0/dialog/oauth?"
            f"client_id={settings.FACEBOOK_APP_ID}"
            f"&redirect_uri={redirect_uri}"
            f"&scope={','.join(scope)}"
            f"&response_type=code"
        )
        return redirect(url)

class FacebookCallbackView(APIView):
    """
    Handles the callback from Facebook after user authentication.
    It exchanges the authorization code for an access token, fetches all the user's
    manageable pages, and stores each page with its own specific access token.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        code = request.query_params.get('code')
        if not code:
            return Response({'error': 'Authorization code not provided.'}, status=400)

        redirect_uri = settings.FACEBOOK_REDIRECT_URI

        # Step 1: Exchange the code for a short-lived user access token.
        token_url = 'https://graph.facebook.com/v19.0/oauth/access_token'
        token_params = {
            'client_id': settings.FACEBOOK_APP_ID,
            'client_secret': settings.FACEBOOK_APP_SECRET,
            'redirect_uri': redirect_uri,
            'code': code,
        }
        r = requests.get(token_url, params=token_params)
        token_data = r.json()

        if 'access_token' not in token_data:
            return Response({'error': 'Failed to retrieve access token.', 'details': token_data}, status=400)

        short_lived_token = token_data['access_token']

        # Step 2: Exchange the short-lived token for a long-lived one.
        long_lived_url = 'https://graph.facebook.com/v19.0/oauth/access_token'
        long_lived_params = {
            'grant_type': 'fb_exchange_token',
            'client_id': settings.FACEBOOK_APP_ID,
            'client_secret': settings.FACEBOOK_APP_SECRET,
            'fb_exchange_token': short_lived_token
        }
        r = requests.get(long_lived_url, params=long_lived_params)
        long_lived_data = r.json()

        if 'access_token' not in long_lived_data:
            return Response({'error': 'Failed to retrieve long-lived token.', 'details': long_lived_data}, status=500)

        long_lived_user_token = long_lived_data['access_token']

        # Step 3: Fetch all pages the user has a role on using the user's token.
        pages_url = f"https://graph.facebook.com/me/accounts"
        pages_params = {
            'access_token': long_lived_user_token
        }
        pages_response = requests.get(pages_url, params=pages_params)
        pages_data = pages_response.json()

        if 'data' not in pages_data:
            return Response({'error': 'Could not retrieve pages for this user.', 'details': pages_data}, status=400)

        # Step 4: Store or update the pages in our database.
        user_profile = request.user.userprofile
        retrieved_pages = []
        for page in pages_data['data']:
            # We only want to save pages where the user has permission to post.
            if 'CREATE_CONTENT' in page.get('tasks', []):
                page_obj, created = FacebookPage.objects.update_or_create(
                    page_id=page['id'],
                    defaults={
                        'user_profile': user_profile,
                        'name': page['name'],
                        'access_token': page['access_token'] # This is the crucial page-specific token
                    }
                )
                retrieved_pages.append({
                    'id': page_obj.id, # Return our database ID for the frontend
                    'page_id': page_obj.page_id,
                    'name': page_obj.name
                })

        return Response({
            'success': 'Facebook account linked and pages retrieved successfully.',
            'pages': retrieved_pages
        })

class UserPagesView(APIView):
    """
    An endpoint for the frontend to fetch the list of pages a user has connected.
    This allows the UI to display a dropdown of pages for the user to choose from.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            user_profile = request.user.userprofile
            pages = user_profile.facebook_pages.all()
            serializer = FacebookPageSerializer(pages, many=True)
            return Response(serializer.data)
        except UserProfile.DoesNotExist:
            return Response({"error": "User profile not found."}, status=404)

