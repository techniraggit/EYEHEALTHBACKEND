from store.models.products import Wishlist, Frame
from django.contrib.gis.geos import Point
from store.models.models import Stores, StoreRating
from store.serializers import StoreSerializer
from core.utils import api_response
from store.views.base import UserMixin


class StoreView(UserMixin):
    def get(self, request):
        stores = Stores.objects.filter(is_active=True)

        stores_data = [
            {
                "id": store.id,
                "name": store.name,
                "distance_km": None,
                "address": store.full_address(),
                "services": [service.name for service in store.services.all()],
                "opening_time": store.store_availability.first().start_working_hr.strftime(
                    "%I:%M %p"
                ),
                "closing_time": store.store_availability.first().end_working_hr.strftime(
                    "%I:%M %p"
                ),
                "rating": store.get_average_rating(),
                "images": [
                    f"{request.build_absolute_uri(i.image.url)}"
                    for i in store.images.all()
                ],
            }
            for store in stores
        ]

        # Serialize and return the response
        return api_response(True, 200, stores=stores_data)


class NearbyStoreView(UserMixin):
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
                "id": store.id,
                "name": store.name,
                "distance_km": round(store.distance.km, 2),  # Convert to km
                "address": store.full_address(),
                "services": [service.name for service in store.services.all()],
                "opening_time": store.store_availability.first().start_working_hr.strftime(
                    "%I:%M %p"
                ),
                "closing_time": store.store_availability.first().end_working_hr.strftime(
                    "%I:%M %p"
                ),
                "latitude": store.latitude,
                "longitude": store.longitude,
                "rating": store.get_average_rating(),
                "images": [
                    f"{request.build_absolute_uri(i.image.url)}"
                    for i in store.images.all()
                ],
            }
            for store in stores
        ]
        return api_response(True, 200, stores=stores_data)

class NearbyStoresMapView(UserMixin):
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
                "id": store.id,
                "name": store.name,
                "latitude": store.latitude,
                "longitude": store.longitude,
                "address": store.full_address(),
            }
            for store in stores
        ]
        return api_response(True, 200, stores=stores_data)


class StoreRatingView(UserMixin):
    def post(self, request, store_id):
        rating = request.data.get("rating")
        review = request.data.get("review")
        try:
            store = Stores.objects.get(id=store_id)
        except:
            return api_response(False, 404, message="Store not found")

        if not rating:
            return api_response(False, 400, message="Rating required")

        if not isinstance(rating, int):
            return api_response(False, 400, message="Rating should be an integer")

        if not 1 <= rating <= 5:
            return api_response(False, 400, message="Rating should be between 1 and 5")

        existing_rating = StoreRating.objects.filter(
            store=store, user=request.user
        ).first()

        if existing_rating:
            existing_rating.rating = rating
            existing_rating.review = review
            existing_rating.save()
            return api_response(True, 200, message="Rating updated successfully")
        else:
            StoreRating.objects.create(
                store=store, user=request.user, rating=rating, review=review
            )
            return api_response(True, 200, message="Rating submitted successfully")


class WishListView(UserMixin):
    def get(self, request):
        data = Wishlist.get_wishlist(request.user)
        return api_response(True, 200, data=data)


class FrameWishListView(UserMixin):
    def post(self, request, frame_id):
        """To add frame to wishlist"""
        try:
            frame = Frame.objects.get(id=frame_id)
        except:
            return api_response(False, 404, message="Frame not found")

        wishlist = Wishlist.objects.filter(user=request.user).first()
        if not wishlist:
            wishlist = Wishlist.objects.create(user=request.user)

        wishlist.frames.add(frame)
        return api_response(True, 200, message="Frame added to wishlist successfully")

    def delete(self, request, frame_id):
        """To remove frame from wishlist"""
        try:
            frame = Frame.objects.get(id=frame_id)
        except Frame.DoesNotExist:
            return api_response(False, 404, message="Frame not found")

        wishlist = Wishlist.objects.filter(user=request.user).first()
        if not wishlist:
            return api_response(False, 404, message="Wishlist not found")

        if frame not in wishlist.frames.all():
            return api_response(False, 400, message="Frame not in wishlist")

        wishlist.frames.remove(frame)
        return api_response(
            True, 200, message="Frame removed from wishlist successfully"
        )


class StoreWishListView(UserMixin):
    def post(self, request, store_id):
        """To store in wishlist"""
        try:
            store = Stores.objects.get(pk=store_id)
        except:
            return api_response(False, 404, message="Store not found")

        wishlist = Wishlist.objects.filter(user=request.user).first()
        if not wishlist:
            wishlist = Wishlist.objects.create(user=request.user)

        wishlist.stores.add(store)

    def delete(self, request, store_id):
        """To remove a store from the wishlist"""
        try:
            store = Stores.objects.get(pk=store_id)
        except Stores.DoesNotExist:
            return api_response(False, 404, message="Store not found")

        wishlist = Wishlist.objects.filter(user=request.user).first()
        if not wishlist:
            return api_response(False, 404, message="Wishlist not found")

        if store not in wishlist.stores.all():
            return api_response(False, 400, message="Store not in wishlist")

        wishlist.stores.remove(store)
        return api_response(
            True, 200, message="Store removed from wishlist successfully"
        )
