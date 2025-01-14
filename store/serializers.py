from store.models.products import Frame
from .models.models import Stores, Services, StoreRating, BusinessModel
from api.models.accounts import UserModel
from rest_framework import serializers


class BaseSerializer(serializers.ModelSerializer):
    def __init__(self, *args, **kwargs):
        fields = kwargs.pop("fields", None)
        super(BaseSerializer, self).__init__(*args, **kwargs)
        if fields is not None:
            allowed_fields = set(fields)
            existing_fields = set(self.fields.keys())
            if len(allowed_fields) == 1 and list(allowed_fields)[0].startswith("-"):
                allowed_fields = {item.replace("-", "") for item in allowed_fields}
                for field_name in existing_fields.intersection(allowed_fields):
                    self.fields.pop(field_name)
            else:
                for field_name in existing_fields - allowed_fields:
                    self.fields.pop(field_name)


class ServicesSerializer(BaseSerializer):
    class Meta:
        model = Services
        fields = "__all__"


class BusinessModelSerializer(BaseSerializer):
    class Meta:
        model = BusinessModel
        fields = "__all__"


class StoreSerializer(BaseSerializer):
    business = BusinessModelSerializer(fields=["id", "name", "phone", "email"])
    services = ServicesSerializer(many=True, fields=["id", "service", "is_paid"])
    store_address = serializers.SerializerMethodField()

    class Meta:
        model = Stores
        fields = "__all__"

    def get_store_address(self, obj):
        return obj.full_address()


class FrameSerializer(BaseSerializer):
    class Meta:
        model = Frame
        fields = "__all__"
