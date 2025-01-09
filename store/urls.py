from django.urls import path
from store import apis

urlpatterns = [
    path("get-stores", apis.StoreView.as_view()),
    path("nearby-stores", apis.NearbyStoreView.as_view()),
    path("stores-rating/<uuid:store_id>", apis.StoreRatingView.as_view()),
]
