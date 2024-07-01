from .base import BaseSerializer
from api.models.dashboard import CarouselModel

class CarouselModelSerializer(BaseSerializer):
    class Meta:
        model = CarouselModel
        fields = "__all__"
    
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        request = self.context.get('request')
        if request:
            representation['image'] = request.build_absolute_uri(instance.image.url)
        else:
            representation['image'] = instance.image.url
        return representation