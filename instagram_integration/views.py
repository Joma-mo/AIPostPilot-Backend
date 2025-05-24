import requests
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import redirect
from users.models import UserProfile
from datetime import datetime, timedelta


class InstagramLoginView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        url = (
            f"https://api.instagram.com/oauth/authorize"
            f"?client_id={settings.INSTAGRAM_APP_ID}"
            f"&redirect_uri={settings.INSTAGRAM_REDIRECT_URI}"
            f"&scope=user_profile,user_media"
            f"&response_type=code"
        )
        return redirect(url)


class InstagramCallbackView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        code = request.query_params.get('code')
        if not code:
            return Response({'error': 'No code provided'}, status=400)

        # Exchange code for access token
        token_url = 'https://api.instagram.com/oauth/access_token'
        data = {
            'client_id': settings.INSTAGRAM_APP_ID,
            'client_secret': settings.INSTAGRAM_APP_SECRET,
            'grant_type': 'authorization_code',
            'redirect_uri': settings.INSTAGRAM_REDIRECT_URI,
            'code': code,
        }
        response = requests.post(token_url, data=data)
        token_data = response.json()

        if 'access_token' not in token_data:
            return Response({'error': 'Token exchange failed', 'details': token_data}, status=400)

        access_token = token_data['access_token']
        user_id = token_data['user_id']

        # Store in UserProfile
        profile = request.user.userprofile
        profile.instagram_id = str(user_id)
        profile.access_token = access_token
        profile.token_expires_at = datetime.now() + timedelta(days=60)
        profile.save()

        return Response({'message': 'Instagram linked successfully'})
