

from rest_framework import serializers
from users.models import FacebookPage

class FacebookPageSerializer(serializers.ModelSerializer):
    """
    Serializer for the FacebookPage model.

    This is used by the UserPagesView to return a list of a user's
    connected pages to the frontend.
    """
    class Meta:
        model = FacebookPage
        # We only need to expose a few fields to the frontend.
        # The 'id' is our internal database ID, which the frontend will use.
        fields = ['id', 'page_id', 'name']

