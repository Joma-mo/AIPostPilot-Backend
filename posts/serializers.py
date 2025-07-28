from rest_framework import serializers
from .models import ScheduledPost
from users.models import FacebookPage # Import the FacebookPage model

class ScheduledPostSerializer(serializers.ModelSerializer):
    """
    Serializer for creating and viewing scheduled posts.

    It now includes a 'facebook_page_id' field that allows the user
    to specify which of their connected pages to post to.
    """
    # This field allows the user to pass our internal DB id for the FacebookPage
    # It's write-only, meaning it's used for creating/updating but not for display.
    facebook_page_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)

    class Meta:
        model = ScheduledPost
        fields = [
            'id',
            'platform',
            'caption',
            'media_url',
            'scheduled_time',
            'status',
            'facebook_page', # The full page object for display (read-only)
            'facebook_page_id' # The ID for creation (write-only)
        ]
        # Make these fields read-only so they can't be set directly by the user
        read_only_fields = ['id', 'status', 'facebook_page']
        # Set the depth to 1 to show nested details of the facebook_page on read.
        depth = 1

    def validate(self, data):
        """
        Custom validation to ensure a page is selected for Facebook posts.
        """
        if data.get('platform') == 'facebook' and not data.get('facebook_page_id'):
            raise serializers.ValidationError("A 'facebook_page_id' is required for Facebook posts.")
        return data

    def create(self, validated_data):
        """
        Custom create method to correctly link the FacebookPage.
        """
        # Get the page_id from the validated data
        page_id = validated_data.pop('facebook_page_id', None)

        # Create the ScheduledPost instance without the page_id
        post = ScheduledPost.objects.create(**validated_data)

        # If a page_id was provided, find the page and link it
        if page_id:
            try:
                # Ensure the selected page belongs to the current user
                page = FacebookPage.objects.get(id=page_id, user_profile=post.user.userprofile)
                post.facebook_page = page
                post.save()
            except FacebookPage.DoesNotExist:
                # If the page doesn't exist or doesn't belong to the user, raise an error
                raise serializers.ValidationError("The selected Facebook Page does not exist or you do not have permission to use it.")

        return post
