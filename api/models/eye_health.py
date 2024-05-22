from .base import BaseModel, models, uuid4
from api.models.accounts import UserModel
from django.contrib.postgres.fields import ArrayField


class UserTestProfile(BaseModel):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    user = models.ForeignKey(UserModel, on_delete=models.CASCADE, related_name="profile")
    full_name = models.CharField(max_length=250, null=True)
    customer_id = models.CharField(max_length=250)
    age = models.CharField(max_length=250)

    def to_json(self):
        return dict(
            id = self.id,
            user = self.user.get_full_name(),
            full_name = self.full_name,
            customer_id = self.customer_id,
            age = self.age,
        )


class UserTest(BaseModel):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    user = models.ForeignKey(
        UserTestProfile, on_delete=models.CASCADE, related_name="eye_test_reports"
    )
    health_score = models.CharField(max_length=50)


class EyeTestReport(BaseModel):
    user_eye_test = models.ForeignKey(
        UserTest, on_delete=models.CASCADE, related_name="eye_test_reports"
    )
    report_id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    id = models.IntegerField()
    full_name = models.CharField(max_length=255)
    mobile = models.CharField(max_length=20)
    feedback = models.TextField(null=True, blank=True)
    face_shape = models.CharField(max_length=255, null=True, blank=True)
    eye_status = models.CharField(max_length=10)
    test = models.CharField(max_length=50)
    choose_astigmatism = models.CharField(max_length=1)
    degree = models.IntegerField()
    myopia_snellen_fraction = models.CharField(max_length=10, null=True, blank=True)
    hyperopia_snellen_fraction = models.CharField(max_length=10, null=True, blank=True)
    myopia_sph_power = models.CharField(max_length=10, null=True, blank=True)
    hyperopia_sph_power = models.CharField(max_length=10, null=True, blank=True)
    cyl_text_size = models.FloatField()
    cyl_power = models.CharField(max_length=10)
    age_power = models.CharField(max_length=10, null=True, blank=True)
    reading_test_snellen_fraction = models.CharField(
        max_length=10, null=True, blank=True
    )
    is_completed = models.BooleanField()
    test_created_at = models.DateTimeField()
    test_of_user = models.IntegerField()
    selected_question = ArrayField(models.IntegerField())

    def __str__(self):
        return self.full_name


class EyeFatigueReport(BaseModel):
    user = models.ForeignKey(
        UserModel, on_delete=models.CASCADE, related_name="eye_fatigue_test_reports"
    )
    is_fatigue_right = models.CharField(max_length=25)
    is_mild_tiredness_right = models.CharField(max_length=25)
    is_fatigue_left = models.CharField(max_length=25)
    is_mild_tiredness_left = models.CharField(max_length=25)

    def __str__(self) -> str:
        return self.full_name
