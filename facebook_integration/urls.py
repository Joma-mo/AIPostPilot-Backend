from django.urls import path
from .views import FacebookLoginView, FacebookCallbackView, UserPagesView

urlpatterns = [
    # This URL starts the login process
    path('login/', FacebookLoginView.as_view(), name='facebook-login'),

    # This is the URL Facebook will redirect back to
    path('callback/', FacebookCallbackView.as_view(), name='facebook-callback'),

    # This is the new endpoint to get a list of the user's pages
    path('pages/', UserPagesView.as_view(), name='facebook-user-pages'),
]
