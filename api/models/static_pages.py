from .base import BaseModel, uuid4, models
from django.contrib.auth import get_user_model
from django.utils.text import slugify

UserModel = get_user_model()

class StaticPages(BaseModel):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    title = models.CharField(max_length=255, unique=True)
    slug = models.SlugField(unique=True)
    content = models.TextField()
    created_by = models.ForeignKey(
        UserModel, on_delete=models.SET_NULL, null=True, blank=True, related_name="static_pages_created_by"
    )
    updated_by = models.ForeignKey(
        UserModel, on_delete=models.SET_NULL, null=True, blank=True, related_name="static_pages_updated_by"
    )

    def to_json(self):
        return dict(
            id=self.id,
            title=self.title,
            content=self.content,
            created_by=self.created_by.get_full_name() if self.created_by else None,
            created_on=self.created_on,
        )
    
    def __str__(self):
        return str(self.id)
    
    def save(self, *args, **kwargs):
        self.slug = self.slug or slugify(self.title)
        super().save(*args, **kwargs)
    
    class Meta:
        ordering = ("-created_on",)
        verbose_name = "Static Page"
        verbose_name_plural = "Static Pages"