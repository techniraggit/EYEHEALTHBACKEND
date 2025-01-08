from django.contrib.gis.geos import Point
from rest_framework.views import APIView
from store.models import Stores
from store.serializers import StoreSerializer
from core.utils import api_response
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication


class UserMixin(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]


class StoreView(APIView):
    def get(self, request):
        stores = Stores.objects.all()
        fields = [
            "company",
            "services",
            "store_address",
            "name",
            "opening_time",
            "closing_time",
            "latitude",
            "longitude",
        ]
        data = StoreSerializer(stores, many=True, fields=fields).data
        return api_response(True, 200, stores=data)


class NearbyStoreView(APIView):
    def get(self, request):
        user_latitude = float(request.GET.get("latitude"))
        user_longitude = float(request.GET.get("longitude"))
        if not user_latitude or not user_longitude:
            return api_response(False, 400, message="Invalid latitude or longitude")

        # Create a Point object for the user's location
        user_location = Point(user_longitude, user_latitude, srid=4326)

        # Fetch nearby stores within 6km radius
        stores = Stores.store_manage.nearby_stores(user_location)

        # Serialize and return the response
        stores_data = [
            {
                "name": store.name,
                "distance_km": round(store.distance.km, 2),  # Convert to km
                "address": store.full_address(),
                "services": [service.name for service in store.services.all()],
                "opening_time": store.opening_time.strftime("%I:%M %p"),
                "closing_time": store.closing_time.strftime("%I:%M %p"),
            }
            for store in stores
        ]
        return api_response(True, 200, stores=stores_data)
