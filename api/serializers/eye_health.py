from .base import BaseSerializer
from api.models.eye_health import UserTestProfile, EyeFatigueReport, EyeTestReport


class UserTestProfileSerializer(BaseSerializer):
    class Meta:
        model = UserTestProfile
        fields = "__all__"


class EyeTestReportSerializer(BaseSerializer):
    class Meta:
        model = EyeTestReport
        fields = "__all__"


class EyeFatigueReportSerializer(BaseSerializer):
    class Meta:
        model = EyeFatigueReport
        fields = "__all__"
