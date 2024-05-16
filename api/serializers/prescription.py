from rest_framework import serializers
from api.models.prescription import UserPrescriptions
from .base import BaseSerializer

class UserPrescriptionsSerializer(BaseSerializer):
    class Meta:
        model = UserPrescriptions
        fields = "__all__"
