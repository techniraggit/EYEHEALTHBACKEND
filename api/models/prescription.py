from .base import BaseModel, models, uuid4
from api.models.accounts import UserModel
from django.core.validators import FileExtensionValidator

image_extensions = [
    "jpg",
    "jpeg",
    "png",
    "bmp",
    "svg",
    "webp",
]


class UserPrescriptions(BaseModel):
    prescription_status = (
        ("pending", "pending"),
        ("approved", "approved"),
        ("rejected", "rejected"),
    )
    prescription_id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    uploaded_file = models.FileField(
        upload_to="user/prescriptions",
        # validators=[FileExtensionValidator(allowed_extensions=image_extensions)],
    )
    status = models.CharField(
        max_length=50, choices=prescription_status, default="pending"
    )
    rejection_notes = models.TextField(default="")
    problem_faced = models.TextField(default="")
    user = models.ForeignKey(
        UserModel, null=True, on_delete=models.SET_NULL, related_name="prescriptions"
    )
