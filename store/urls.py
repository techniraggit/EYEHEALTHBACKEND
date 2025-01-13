from django.urls import path, include
from store.views import apis, booking

booking_urls = [
    path("time-slots", booking.TimeSlotsView.as_view()),
    path("book-appointment/<int:slot_id>", booking.BookAppointmentView.as_view()),
]

urlpatterns = [
    path("get-stores", apis.StoreView.as_view()),
    path("nearby-stores", apis.NearbyStoreView.as_view()),
    path("stores-rating/<uuid:store_id>", apis.StoreRatingView.as_view()),
    path("booking/", include(booking_urls)),
]
