from django.urls import path
from administrator.views import *
from .views import (
    StoreAvailabilityView,
    StoreAvailabilityDetailView,
    StoreDetailView,
    DaysListView,
    HolidaysListView,
    HolidaysDetailView,
    TimingListView,
    TimingDetailView,
    CompleteStoreDetailView,
    CombineListView,
    ServiceListView,
    ServiceDetailView,
    StoreDetailListView,
    StoreServiceListView,
    StoreServiceDetailView,
    StoreappointmentListView,
    StoreServieView,
    StoreAppoitmentView
)


urlpatterns = [
    path("store-detail/<int:pk>", StoreDetailView.as_view()),
    path("store-detail", StoreDetailListView.as_view()),

    path("store-availability", StoreAvailabilityView.as_view()),
    path("store-availability/<int:pk>", StoreAvailabilityDetailView.as_view()),

    path("days", DaysListView.as_view()),

    path("holidays", HolidaysListView.as_view()),
    path("holidays/<int:pk>", HolidaysDetailView.as_view()),

    path("service", ServiceListView.as_view()),
    path("service/<int:pk>", ServiceDetailView.as_view()),

    path("CompleteStoreDetailView/<int:pk>", CompleteStoreDetailView.as_view()),


    # path("utility1", CombineAPIView1.as_view()),
    path("utility1", CombineListView.as_view()),

    path("timing", TimingListView.as_view()),
    path("timing/<int:pk>", TimingDetailView.as_view()),

    path("service_add_store", StoreServiceListView.as_view()),
    path("service_add_store/<int:pk>", StoreServiceDetailView.as_view()),
    path("store_book_appointment", StoreappointmentListView.as_view()),
    path("store_appointment", StoreAppoitmentView.as_view()),
    path("store-services/<int:pk>", StoreServieView.as_view()),
]
