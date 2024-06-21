from .base import BaseModel, uuid4, models
from api.models.accounts import UserModel


class PrivacyPolicy(BaseModel):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    content = models.TextField()
    created_by = models.ForeignKey(
        UserModel, on_delete=models.SET_NULL, null=True, blank=True
    )

    def to_json(self):
        return dict(
            id=self.id,
            content=self.content,
            created_on=self.created_on,
        )

    class Meta:
        ordering = ("-created_on",)
        verbose_name = "Privacy Policy"
        verbose_name_plural = "Privacy Policies"


class TermsAndConditions(BaseModel):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    content = models.TextField()
    created_by = models.ForeignKey(
        UserModel, on_delete=models.SET_NULL, null=True, blank=True
    )

    def to_json(self):
        return dict(
            id=self.id,
            content=self.content,
            created_on=self.created_on,
        )

    class Meta:
        ordering = ("-created_on",)
        verbose_name = "Terms and Conditions"
        verbose_name_plural = "Terms and Conditions"
        