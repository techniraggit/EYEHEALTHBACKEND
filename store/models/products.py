from store.models.base import BaseModel, models
from store.models.models import Stores
from django.conf import settings


class FrameTypes(models.Model):
    name = models.CharField(max_length=100, unique=True)

    class Meta:
        verbose_name_plural = "Frame Types"
        verbose_name = "Frame Type"
        ordering = ["name"]

    def __str__(self):
        return f"{self.name}"

    def save(self, *args, **kwargs):
        if not self.pk:
            self.name = self.name.lower()
        super().save(*args, **kwargs)


class Brands(models.Model):
    name = models.CharField(max_length=100, unique=True)

    class Meta:
        verbose_name_plural = "Brands"
        verbose_name = "Brand"
        ordering = ["name"]

    def __str__(self):
        return f"{self.name}"

    def save(self, *args, **kwargs):
        if not self.pk:
            self.name = self.name.upper()
        super().save(*args, **kwargs)


class Gender:
    Men = "Men"
    Women = "Women"
    Unisex = "Unisex"
    Kids = "Kids"
    choices = (
        (Men, Men),
        (Women, Women),
        (Unisex, Unisex),
        (Kids, Kids),
    )


class Frame(BaseModel):
    name = models.CharField(max_length=100)
    frame_type = models.ForeignKey(
        FrameTypes,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="frame_type",
    )
    gender = models.CharField(max_length=10, choices=Gender.choices)
    brand = models.ForeignKey(
        Brands,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="frame_brand",
    )
    image = models.FileField(upload_to=f"frames")
    is_recommended = models.BooleanField(default=False)

    class Meta:
        verbose_name_plural = "Frames"
        verbose_name = "Frame"

    def to_json(self, request=None):
        img_path = self.image.url if self.image else "/"
        if request:
            img_path = request.build_absolute_uri(img_path)

        return {
            "id": self.id,
            "name": self.name,
            "frame_type": self.frame_type.name,
            "gender": self.gender,
            "brand": self.brand.name,
            "image": img_path,
            "is_recommended": "Yes" if self.is_recommended else "No",
        }

    def __str__(self):
        return self.name

    @classmethod
    def get_recommended_frames(cls):
        return cls.objects.filter(is_recommended=True)


class Wishlist(BaseModel):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="wishlist",
    )
    frames = models.ManyToManyField(Frame, related_name="wishlist_frames")
    stores = models.ManyToManyField(Stores, related_name="wishlist_stores")

    @classmethod
    def get_wishlist(cls, user):
        qs = cls.objects.filter(user=user)
        data = []
        for wishlist in qs:
            frames = wishlist.frames.all()
            stores = wishlist.stores.all()

            for frame in frames:
                data.append(
                    {
                        "Type": "frame",
                        "Data": frame.to_json(),
                    }
                )

            for store in stores:
                data.append(
                    {
                        "Type": "store",
                        "Data": store.to_json(),
                    }
                )

        return data

    class Meta:
        verbose_name_plural = "Favorite Frames"
        verbose_name = "Favorite Frame"
