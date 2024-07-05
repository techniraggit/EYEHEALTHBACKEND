from api.models.static_pages import StaticPages
from .base import BaseSerializer, serializers
from django.contrib.auth import get_user_model

UserModel = get_user_model()

class StaticPagesSerializer(BaseSerializer):
    created_by = serializers.PrimaryKeyRelatedField(queryset=UserModel.objects.all(), required=False, allow_null=True)
    updated_by = serializers.PrimaryKeyRelatedField(queryset=UserModel.objects.all(), required=False, allow_null=True)

    class Meta:
        model = StaticPages
        fields = ['id', 'title', 'content', 'created_by', 'updated_by']
        read_only_fields = ['id']

    def create(self, validated_data):
        validated_data['created_by'] = self.context['request'].user
        validated_data['updated_by'] = self.context['request'].user
        return super().create(validated_data)

    def update(self, instance, validated_data):
        validated_data['updated_by'] = self.context['request'].user
        return super().update(instance, validated_data)