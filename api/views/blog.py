from .base import UserMixin
from api.models.blog import BlogModel
from api.serializers.blog import BlogSerializer
from core.utils import api_response


class BlogListingView(UserMixin):
    def get(self, request):
        blog_qs = BlogModel.objects.filter(is_active=True)
        blog_data = BlogSerializer(blog_qs, many=True).data
        return api_response(True, 200, data=blog_data)

class BlogDetailView(UserMixin):
    def get(self, request, blog_id):
        print("BLogID", blog_id)
        try:
            blog_qs = BlogModel.objects.get(id=blog_id)
            blog_data = BlogSerializer(blog_qs, fields=["title", "content", "image", "created_on"]).data
            return api_response(True, 200, data=blog_data)
        except BlogModel.DoesNotExist:
            return api_response(False, 404, message="Blog not found.")