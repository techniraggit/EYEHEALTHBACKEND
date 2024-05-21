from .base import BaseSerializer, serializers
from api.models.eye_health import UserEyeTest, TestReport


class TestReportSerializer(BaseSerializer):
    class Meta:
        model = TestReport
        fields = "__all__"

class UserEyeTestSerializer(BaseSerializer):
    test_reports = TestReportSerializer(many=True, read_only=True)
    class Meta:
        model = UserEyeTest
        fields = "__all__"