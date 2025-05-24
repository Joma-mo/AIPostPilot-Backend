from django.urls import path
from .views import RecommendedTimesView

urlpatterns = [
    path('post-times/', RecommendedTimesView.as_view(), name='recommended-times'),
]
