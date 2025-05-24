from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from datetime import datetime, timedelta


class RecommendedTimesView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        now = datetime.utcnow()
        user = request.user

        # 🧠 Mock AI logic – you can later replace with real ML model
        suggested_times = [
            (now + timedelta(days=i, hours=18)).isoformat() + "Z"
            for i in range(3)
        ]

        return Response({
            "user_id": user.id,
            "recommended_times": suggested_times,
            "note": "These are the best times for posting."
        })
