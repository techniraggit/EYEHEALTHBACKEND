from .base import BaseModel, models
from .accounts import UserModel
from django.urls import reverse
from uuid import uuid4


class BlogModel(BaseModel):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    title = models.CharField(max_length=255)
    content = models.TextField()
    image = models.FileField(upload_to="blog/images/")
    author = models.ForeignKey(
        UserModel, on_delete=models.SET_NULL, null=True, related_name="created_blogs"
    )
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("blog_detail_view", kwargs={"blog_id": self.id})

    class Meta:
        ordering = ("-created_on",)
