from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ScheduledPostViewSet

# A router automatically generates the URL patterns for a ViewSet.
# This handles the list, create, retrieve, update, and destroy actions.
router = DefaultRouter()
router.register(r'', ScheduledPostViewSet, basename='scheduledpost')

# The API URLs are now determined automatically by the router.
urlpatterns = [
    path('', include(router.urls)),
]
