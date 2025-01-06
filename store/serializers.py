from .models import (
    Services,
    Days,
    Holiday,
    Timing,
    StoreAvail,
    Store,
    StoreDetail,
)
from core.serializers import serializers
from retailer.serializers import StoreSerializer


class ServiceSerializer(BaseSerializer):
    class Meta:
        model = Services
        fields = "__all__"


class DaysSerializer(BaseSerializer):
    class Meta:
        model = Days
        # fields = ('day',)
        fields = ("id", "day")


class HolidaysSerializer(BaseSerializer):
    class Meta:
        model = Holiday
        # fields = ('day',)
        fields = "__all__"


class TimingSerializer(BaseSerializer):
    class Meta:
        model = Timing
        # fields = ('day',)
        fields = "__all__"

    def validate(self, data):
        """
        Check that start is before finish.
        """
        if data["start_time"] >= data["end_time"]:
            raise serializers.ValidationError(
                "Start time should be less than End time."
            )
        return data


class DayListingField(serializers.RelatedField):
    def to_representation(self, value):
        return value.day


class StoreAvailSerializer(BaseSerializer):
    store = serializers.PrimaryKeyRelatedField(queryset=Store.objects.all())
    day = serializers.PrimaryKeyRelatedField(queryset=Days.objects.all())
    timing = serializers.PrimaryKeyRelatedField(queryset=Timing.objects.all())

    class Meta:
        model = StoreAvail
        # fields = ('store', 'day', 'start_time', 'end_time')
        fields = "__all__"
        depth = 1


class StoreAvailSerializer2(BaseSerializer):
    store = StoreSerializer(read_only=True)
    day = DaysSerializer(read_only=True)
    timing = TimingSerializer(read_only=True)

    class Meta:
        model = StoreAvail
        # fields = ('store', 'day', 'start_time', 'end_time')
        fields = "__all__"
        depth = 1


# class StoreAvailabilitySerializer(BaseSerializer):
#     store = serializers.PrimaryKeyRelatedField(queryset=Store.objects.all())
#     day = serializers.PrimaryKeyRelatedField(queryset=Days.objects.all(), many=True)
#
#     class Meta:
#         model = StoreAvailability
#         fields = ("store", "day", "start_time", "end_time")
#         # fields = '__all__'
#         depth = 1

# def validate(self, data):
#     """
#     Check that start is before finish.
#     """
#     if data["start_time"] >= data["end_time"]:
#         raise serializers.ValidationError(
#             "Start time should be less than End time."
#         )
#     return data


# class StoreAvailabilityGetSerializer(BaseSerializer):
#     store = StoreSerializer(read_only=True)
#     day = DaysSerializer(read_only=True, many=True)
#
#     class Meta:
#         model = StoreAvailability
#         fields = ("store", "day", "start_time", "end_time")
#         # fields = '__all__'
#         depth = 1


# class StoreAvailabilityCreateSerializer(BaseSerializer):
#     # store = StoreSerializer(read_only=True)
#     # day = DaysSerializer(read_only=True, many=True)
#
#     class Meta:
#         model = StoreAvailability
#         fields = ("store", "day", "start_time", "end_time")
#         # fields = '__all__'
#         # depth = 2

# def validate(self, data):
#     """
#     Check that start is before finish.
#     """
#     if data["start_time"] < data["end_time"]:
#         raise serializers.ValidationError(
#             "Start time should be less than End time."
#         )
#     return data


class StoreDetailSerializer(BaseSerializer):

    class Meta:
        model = StoreDetail
        fields = [
            "id",
            "store",
            "description",
            "phone",
            "location",
            "images",
        ]


class StoreDetailCreateSerializer(BaseSerializer):
    class Meta:
        model = StoreDetail
        fields = ("store", "description", "phone", "location", "images")
        # fields = '__all__'


class CompleteStoreDetailSerializer(BaseSerializer):
    store = StoreSerializer()
    services = ServiceSerializer(read_only=True, many=True)

    class Meta:
        model = StoreDetail
        fields = "__all__"


class CombineSerializer(BaseSerializer):
    services = ServiceSerializer(read_only=True, many=True)
    timings = TimingSerializer(read_only=True, many=True)
    holidays = HolidaysSerializer(read_only=True, many=True)
    days = DaysSerializer(read_only=True, many=True)

    class Meta:
        model = Store
        fields = ("services", "timings", "holidays", "days")


class StoreServiceCreateSerializer(serializers.Serializer):
    store_id = serializers.IntegerField()
    services = serializers.ListField(child=serializers.IntegerField())

    # class Meta:
    #     model = StoreDetail
    #     fields = ('store_id', 'services')


# services = ServiceSerializer(read_only=True, many=True)


class StoreServiceUpdateSerializer(serializers.ModelSerializer):
    pass


class StoreServiceDetailSerializer(serializers.ModelSerializer):
    services = ServiceSerializer(read_only=True, many=True)

    class Meta:
        model = StoreDetail
        fields = ("store", "services")
