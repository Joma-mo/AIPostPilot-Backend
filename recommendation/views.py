from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import EngagementLog
from .engine import recommend_post_times

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_recommendation(request):
    logs = EngagementLog.objects.filter(user=request.user)
    best_hours = recommend_post_times(logs)
    return Response({"recommended_hours": best_hours})
