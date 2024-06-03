from django.urls import path, include
from .views.auth import *
from .views.home import *
from .views.users import *
from .views.offers import *
from .views.prescription import *
from .views.notifications import *
from .views.subscription import *

auth_urls = [
    path("", LoginView.as_view(), name="login_view"),
    path("logout", LogoutView.as_view(), name="logout_view"),
]

home_urls = [
    path("", HomeView.as_view(), name="home_view"),
]

users_urls = [
    path("", UserView.as_view(), name="users_view"),
    path("user-view", UserDetailView.as_view(), name="user_detailed_view"),
]

offers_urls = [
    path("", OffersView.as_view(), name="offers_view"),
    path("redeemed-offers", RedeemedOffersView.as_view(), name="redeemed_offers_view"),
]

prescription_urls = [
    path("", PrescriptionView.as_view(), name="prescription_view"),
]

notification_urls = [
    path("", NotificationView.as_view(), name="notification_view"),
]


subscription_urls = [
    path("", SubscriptionView.as_view(), name="subscription_view"),
]

urlpatterns = [
    path("", include(auth_urls)),
    path("home/", include(home_urls)),
    path("users/", include(users_urls)),
    path("offers/", include(offers_urls)),
    path("prescription/", include(prescription_urls)),
    path("notification/", include(notification_urls)),
    path("subscription/", include(subscription_urls)),
]
