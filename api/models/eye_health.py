from django.db.models import JSONField
from .base import BaseModel, models, uuid4
from api.models.accounts import UserModel


class UserTestProfile(BaseModel):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    user = models.ForeignKey(
        UserModel, on_delete=models.CASCADE, related_name="profiles"
    )
    full_name = models.CharField(max_length=250, null=True)
    customer_id = models.CharField(max_length=250)
    age = models.CharField(max_length=250)

    def to_json(self):
        return dict(
            id=self.id,
            user=self.user.get_full_name(),
            full_name=self.full_name,
            customer_id=self.customer_id,
            age=self.age,
        )


class EyeTestReport(BaseModel):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    report_id = models.IntegerField(unique=True)
    user_profile = models.ForeignKey(UserTestProfile, on_delete=models.CASCADE)
    right_eye = JSONField()
    left_eye = JSONField()
    health_score = models.FloatField()

    def to_json(self):
        return dict(
            id=self.id,
            report_id=self.report_id,
            user_profile=self.user_profile.to_json(),
            right_eye=self.right_eye,
            left_eye=self.left_eye,
            health_score=self.health_score,
        )


class EyeFatigueReport(BaseModel):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    user = models.ForeignKey(
        UserModel, on_delete=models.CASCADE, related_name="eye_fatigue_test_reports"
    )
    report_id = models.IntegerField(unique=True)
    is_fatigue_right = models.BooleanField()
    is_mild_tiredness_right = models.BooleanField()
    is_fatigue_left = models.BooleanField()
    is_mild_tiredness_left = models.BooleanField()

    def __str__(self) -> str:
        return self.user.get_full_name()

    def to_json(self):
        return dict(
            id=self.id,
            user=self.user.get_full_name(),
            report_id=self.report_id,
            is_fatigue_right=self.is_fatigue_right,
            is_mild_tiredness_right=self.is_mild_tiredness_right,
            is_fatigue_left=self.is_fatigue_left,
            is_mild_tiredness_left=self.is_mild_tiredness_left,
        )

    def get_percent(self):
        return (4 - (self.is_fatigue_right + self.is_mild_tiredness_right + self.is_fatigue_left + self.is_mild_tiredness_left)) * 100 / 4

