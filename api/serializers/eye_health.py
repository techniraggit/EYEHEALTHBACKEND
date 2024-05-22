from .base import BaseSerializer, serializers
from api.models.eye_health import UserTestProfile


class UserTestProfileSerializer(BaseSerializer):
    class Meta:
        model = UserTestProfile
        fields = "__all__"