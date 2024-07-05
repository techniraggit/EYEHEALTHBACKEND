from .base import APIView
from api.models.static_pages import StaticPages
from core.utils import api_response
from rest_framework.views import APIView
from api.serializers.user_agreement import StaticPagesSerializer


class StaticPagesView(APIView):
    def get(self, request):
        static_pages = StaticPages.objects.all().order_by("-created_on")
        serializer = StaticPagesSerializer(static_pages, many=True, fields=["title", "content"])
        return api_response(True, 200, data=serializer.data)
