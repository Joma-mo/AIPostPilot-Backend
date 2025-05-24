from django.urls import path
from .views import get_recommendation

urlpatterns = [
    path('recommendation/', get_recommendation),
]
