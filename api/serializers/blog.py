from .base import BaseSerializer, serializers
from api.models.blog import BlogModel


class BlogSerializer(BaseSerializer):
    abs_url = serializers.SerializerMethodField()
    class Meta:
        model = BlogModel
        fields = ["id", "title", "content", "image", "abs_url", "created_on"]
    
    def get_abs_url(self, obj):
        return obj.get_absolute_url()