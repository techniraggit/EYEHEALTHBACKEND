from django.urls import path, include
from store.views import apis, booking, products

booking_urls = [
    path("time-slots", booking.TimeSlotsView.as_view()),
    path("book-appointment/<int:slot_id>", booking.BookAppointmentView.as_view()),
    path("booked-appointment", booking.BookedAppointmentsView.as_view()),
]

product_urls = [
    path("frames", products.FramesView.as_view()),
]

urlpatterns = [
    path("get-stores", apis.StoreView.as_view()),
    path("nearby-stores", apis.NearbyStoreView.as_view()),
    path("nearby-stores-map", apis.NearbyStoresMapView.as_view()),
    path("stores-rating/<uuid:store_id>", apis.StoreRatingView.as_view()),
    path("wishlist", apis.WishListView.as_view()),
    path("frame-wishlist/<int:frame_id>", apis.FrameWishListView.as_view()),
    path("store-wishlist/<uuid:store_id>", apis.StoreWishListView.as_view()),
    path("booking/", include(booking_urls)),
    path("products/", include(product_urls)),
]
