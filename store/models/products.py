from store.models.base import BaseModel, models
from store.models.models import Stores
from django.conf import settings


class FrameType:
    AVIATOR = "AVIATOR"
    CLUBMASTER = "CLUBMASTER"
    HEXAGON = "HEXAGON"
    OVAL = "OVAL"
    ROUND = "ROUND"
    SQUARE = "SQUARE"
    CATEYE = "CATEYE"
    RECTANGLE = "RECTANGLE"
    WAYFARER = "WAYFARER"

    CHOICES = (
        (AVIATOR, AVIATOR),
        (CLUBMASTER, CLUBMASTER),
        (HEXAGON, HEXAGON),
        (OVAL, OVAL),
        (ROUND, ROUND),
        (SQUARE, SQUARE),
        (CATEYE, CATEYE),
        (RECTANGLE, RECTANGLE),
        (WAYFARER, WAYFARER),
    )


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


class Brand:
    RayBan = "RayBan"
    Gucci = "Gucci"
    Prada = "Prada"

    choices = (
        (RayBan, RayBan),
        (Gucci, Gucci),
        (Prada, Prada),
    )


class Frame(BaseModel):
    name = models.CharField(max_length=100)
    frame_type = models.CharField(max_length=50, choices=FrameType.CHOICES)
    gender = models.CharField(max_length=10, choices=Gender.choices)
    brand = models.CharField(max_length=10, choices=Brand.choices)
    image = models.FileField(upload_to=f"frames")
    is_recommended = models.BooleanField(default=False)

    class Meta:
        verbose_name_plural = "Frames"
        verbose_name = "Frame"

    def to_json(self):
        return {
            "name": self.name,
            "frame_type": self.frame_type,
            "gender": self.gender,
            "brand": self.brand,
            "image": self.image.url if self.image else None,
            "is_recommended": self.is_recommended,
        }


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
