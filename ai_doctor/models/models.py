from .base import BaseModel, models
from api.models.accounts import UserModel


class ChatHistory(BaseModel):
    user = models.ForeignKey(
        UserModel, on_delete=models.SET_NULL, null=True, related_name="ai_chat_history"
    )
    query = models.TextField()
    response = models.TextField()

    class Meta:
        ordering = ["-created_at"]
        verbose_name_plural = "Chat History"
        verbose_name = "Chat History"
