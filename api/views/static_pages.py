from .base import APIView
from api.models.static_pages import StaticPages
from core.utils import api_response
from rest_framework.views import APIView
from api.serializers.user_agreement import StaticPagesSerializer


class StaticPagesView(APIView):
    def get(self, request, slug):
        try:
            static_page = StaticPages.objects.get(slug=slug)
            serializer = StaticPagesSerializer(static_page, fields=["title", "content"])
            return api_response(True, 200, content=serializer.data["content"])
        except StaticPages.DoesNotExist:
            return api_response(False, 404, "Static page not found")


class StaticPagesSlugView(APIView):
    def get(self, request):
        generated_slug = StaticPages.objects.all().values("title", "slug")
        return api_response(True, 200, generated_slug=generated_slug)
