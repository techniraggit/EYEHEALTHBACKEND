from .base import BaseModel, models, uuid4
from api.models.accounts import UserModel

class UserPrescriptions(BaseModel):
    prescription_status = (
        ("pending", "pending"),
        ("approved", "approved"),
        ("rejected", "rejected"),
    )
    prescription_id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    file = models.FileField(upload_to="user/prescriptions")
    status = models.CharField(max_length=50, choices=prescription_status, default="pending")
    text = models.TextField(blank=True, null=True)
    user = models.ForeignKey(UserModel, null=True, on_delete=models.SET_NULL, related_name="prescriptions")