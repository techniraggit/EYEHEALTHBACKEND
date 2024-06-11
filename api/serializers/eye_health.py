from .base import BaseSerializer, serializers
from api.models.eye_health import UserTestProfile, EyeFatigueReport, EyeTestReport
from api.serializers.accounts import ProfileSerializer


class UserTestProfileSerializer(BaseSerializer):
    class Meta:
        model = UserTestProfile
        fields = "__all__"


class EyeTestReportSerializer(BaseSerializer):
    user_profile = UserTestProfileSerializer(fields=["full_name", "age"])

    class Meta:
        model = EyeTestReport
        fields = "__all__"


class EyeFatigueReportSerializer(BaseSerializer):
    user = ProfileSerializer(read_only=True, fields=["first_name", "last_name", "age"])
    suggestion = serializers.SerializerMethodField()
    percentage = serializers.SerializerMethodField()

    class Meta:
        model = EyeFatigueReport
        fields = "__all__"

    def get_suggestion(self, object):
        return object.suggestion

    def get_percentage(self, object):
        return object.health_score
