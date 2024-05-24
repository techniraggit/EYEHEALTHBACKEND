from .base import BaseSerializer
from api.models.eye_health import UserTestProfile, EyeFatigueReport


class UserTestProfileSerializer(BaseSerializer):
    class Meta:
        model = UserTestProfile
        fields = "__all__"


class EyeFatigueReportSerializer(BaseSerializer):
    class Meta:
        model = EyeFatigueReport
        fields = "__all__"

    # def to_representation(self, instance):
    #     representation = super().to_representation(instance)
    #     fields = [
    #         "is_fatigue_right",
    #         "is_mild_tiredness_right",
    #         "is_fatigue_left",
    #         "is_mild_tiredness_left",
    #     ]
    #     for field in fields:
    #         representation[field] = "Yes" if getattr(instance, field) else "No"
    #     return representation
