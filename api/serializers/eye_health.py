from .base import BaseSerializer, serializers
from api.models.eye_health import UserTestProfile, EyeFatigueReport, EyeTestReport
from api.serializers.accounts import ProfileSerializer


class UserTestProfileSerializer(BaseSerializer):
    class Meta:
        model = UserTestProfile
        fields = "__all__"


class EyeTestReportSerializer(BaseSerializer):
    class Meta:
        model = EyeTestReport
        fields = "__all__"


class EyeFatigueReportSerializer(BaseSerializer):
    user = ProfileSerializer(read_only=True, fields=["first_name", "last_name", "age"])
    suggestion = serializers.SerializerMethodField()

    class Meta:
        model = EyeFatigueReport
        fields = "__all__"

    def get_suggestion(self, object):
        suggestion = "Great job! Your eye health is in good shape. Continue practicing healthy habits like staying well-hydrated and taking short breaks during screen time."
        return suggestion
