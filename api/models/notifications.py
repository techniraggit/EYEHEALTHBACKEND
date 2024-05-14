from api.models.accounts import UserModel
from django.db import models
from api.models.base import BaseModel


class PushNotification(BaseModel):
    users = models.ManyToManyField(UserModel, through="UserPushNotification")
    title = models.CharField(max_length=100)
    message = models.TextField()

    def __str__(self):
        return str(self.title)


class UserPushNotification(BaseModel):
    user = models.ForeignKey(UserModel, on_delete=models.CASCADE)
    notification = models.ForeignKey(PushNotification, on_delete=models.CASCADE)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user} - {self.notification.title}"
