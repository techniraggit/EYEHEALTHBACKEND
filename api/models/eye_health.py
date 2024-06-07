from core.constants import FATIGUE_SUGGESTIONS_AND_HEALTH_SCORES
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

    def eye_obj(self, eye):
        return {
            "sph": eye.get("hyperopia_sph_power", eye.get("myopia_sph_power")),
            "cyl": eye.get("cyl_power"),
            "axis": eye.get("degree"),
            "add": eye.get("age_power"),
        }

    def left_eye_obj(self):
        return self.eye_obj(self.left_eye)

    def right_eye_obj(self):
        return self.eye_obj(self.right_eye)

    def report(self):
        return dict(
            report_id=self.report_id,
            name=self.user_profile.full_name,
            age=self.user_profile.age,
            right=self.right_eye_obj(),
            left=self.left_eye_obj(),
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
            full_name=self.user.get_full_name(),
            age=self.user.age(),
            report_id=self.report_id,
            is_fatigue_right=self.is_fatigue_right,
            is_mild_tiredness_right=self.is_mild_tiredness_right,
            is_fatigue_left=self.is_fatigue_left,
            is_mild_tiredness_left=self.is_mild_tiredness_left,
        )

    def get_percent(self):
        score, _ = self.get_values()
        return score

    def get_suggestions(self):
        _, suggestion = self.get_values()
        return suggestion

    def get_score_and_suggestions(
        self,
        is_fatigue_right,
        is_mild_tiredness_right,
        is_fatigue_left,
        is_mild_tiredness_left,
    ):
        for condition in FATIGUE_SUGGESTIONS_AND_HEALTH_SCORES:
            if (
                condition["is_fatigue_right"] == is_fatigue_right
                and condition["is_mild_tiredness_right"] == is_mild_tiredness_right
                and condition["is_fatigue_left"] == is_fatigue_left
                and condition["is_mild_tiredness_left"] == is_mild_tiredness_left
            ):
                return condition["health_score"], condition["suggestion"]

        return (
            0,
            "Your condition does not match any predefined criteria. Please consult your eye doctor.",
        )

    def get_values(self):
        return self.get_score_and_suggestions(
            self.is_fatigue_right,
            self.is_mild_tiredness_right,
            self.is_fatigue_left,
            self.is_mild_tiredness_left,
        )
