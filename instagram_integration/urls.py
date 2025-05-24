from django.urls import path
from .views import InstagramLoginView, InstagramCallbackView

urlpatterns = [
    path('login/', InstagramLoginView.as_view(), name='instagram-login'),
    path('callback/', InstagramCallbackView.as_view(), name='instagram-callback'),
]
