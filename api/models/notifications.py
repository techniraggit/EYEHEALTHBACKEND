from api.models.accounts import UserModel
from django.db import models
from api.models.base import BaseModel
from uuid import uuid4


class PushNotification(BaseModel):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    users = models.ManyToManyField(UserModel, through="UserPushNotification")
    title = models.CharField(max_length=100)
    message = models.TextField()

    def __str__(self):
        return str(self.title)


class UserPushNotification(BaseModel):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    user = models.ForeignKey(UserModel, on_delete=models.CASCADE)
    notification = models.ForeignKey(PushNotification, on_delete=models.CASCADE)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user} - {self.notification.title}"
