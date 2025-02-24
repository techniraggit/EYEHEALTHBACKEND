from django.db.models import JSONField
from .base import BaseModel, models, uuid4
from api.models.accounts import UserModel


class UserTestProfile(BaseModel):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    customer_id = models.CharField(max_length=250, null=True, blank=True)
    user = models.ForeignKey(
        UserModel, on_delete=models.CASCADE, related_name="profiles"
    )
    full_name = models.CharField(max_length=250, null=True)
    age = models.CharField(max_length=250)
    email = models.EmailField(null=True, blank=True)
    phone_number = models.CharField(max_length=20, null=True, blank=True)

    def to_json(self):
        return dict(
            id=self.id,
            user=self.user.get_full_name(),
            full_name=self.full_name,
            customer_id=self.customer_id,
            age=self.age,
        )


    def __str__(self):
        return f"{self.full_name}/{self.phone_number}/{self.email}"


class EyeTestReport(BaseModel):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    report_id = models.IntegerField(unique=True)
    user_profile = models.ForeignKey(UserTestProfile, on_delete=models.CASCADE)
    right_eye = JSONField()
    left_eye = JSONField()
    health_score = models.FloatField()
    colour_contrast = models.CharField(max_length=30, null=True, blank=True)
    color_blindness = models.CharField(max_length=30, null=True, blank=True)

    def to_json(self):
        return dict(
            id=self.id,
            report_id=self.report_id,
            user_profile=self.user_profile.to_json(),
            right_eye=self.right_eye,
            left_eye=self.left_eye,
            health_score=self.health_score,
            colour_contrast=self.colour_contrast,
            color_blindness=self.color_blindness,
        )

    def eye_obj(self, eye):
        sph = eye.get("sph_power", None)
        cyl = eye.get("cyl_power", None)
        axis = eye.get("axis", None)
        add = eye.get("add_power", None)
        if all([sph, cyl, axis, add]):
            return {
                "sph": sph,
                "cyl": cyl,
                "axis": axis,
                "add": add,
            }
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
            colour_contrast=self.colour_contrast,
            color_blindness=self.color_blindness,
        )


class EyeFatigueReport(BaseModel):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    user = models.ForeignKey(
        UserModel, on_delete=models.CASCADE, related_name="eye_fatigue_test_reports"
    )
    full_name = models.CharField(max_length=255, default="")
    age = models.CharField(max_length=255, default="")
    report_id = models.IntegerField(unique=True)
    is_fatigue_right = models.BooleanField()
    is_mild_tiredness_right = models.BooleanField()
    is_fatigue_left = models.BooleanField()
    is_mild_tiredness_left = models.BooleanField()
    health_score = models.IntegerField(default=0)
    suggestion = models.TextField(default="")

    def __str__(self) -> str:
        return self.user.get_full_name()

    def to_json(self):
        return dict(
            id=self.id,
            full_name=self.full_name,
            age=self.age,
            report_id=self.report_id,
            is_fatigue_right=self.is_fatigue_right,
            is_mild_tiredness_right=self.is_mild_tiredness_right,
            is_fatigue_left=self.is_fatigue_left,
            is_mild_tiredness_left=self.is_mild_tiredness_left,
        )

    def get_percent(self):
        return self.health_score

    def get_suggestions(self):
        return self.suggestion