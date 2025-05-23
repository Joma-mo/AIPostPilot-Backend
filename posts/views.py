from rest_framework import generics, permissions
from .models import ScheduledPost
from .serializers import ScheduledPostSerializer


class PostListCreateView(generics.ListCreateAPIView):
    serializer_class = ScheduledPostSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return ScheduledPost.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class PostRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ScheduledPostSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return ScheduledPost.objects.filter(user=self.request.user)
