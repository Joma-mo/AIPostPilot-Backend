from rest_framework import viewsets, permissions
from .models import ScheduledPost
from .serializers import ScheduledPostSerializer

class ScheduledPostViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to create, view, and manage their scheduled posts.
    """
    # Use the updated serializer that handles dynamic page selection
    serializer_class = ScheduledPostSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """
        This view should only return posts created by the currently authenticated user.
        """
        return ScheduledPost.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        """
        When a new post is created, automatically associate it with the
        currently authenticated user.
        """
        serializer.save(user=self.request.user)
