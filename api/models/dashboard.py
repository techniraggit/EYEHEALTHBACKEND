from .base import BaseModel, models, uuid4


class CarouselModel(BaseModel):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    image = models.FileField(upload_to="carousel/images/")
    name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)

    def __str__(self) -> str:
        return self.name

    def to_json(self, request):
        return dict(
            id=self.id,
            image=request.build_absolute_uri(self.image.url),
            name=self.name,
            is_active=self.is_active,
        )