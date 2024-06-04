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
    path("user-view/<uuid:id>", UserDetailedView.as_view(), name="user_detailed_view"),
    path("user-edit/<uuid:id>", UserEditView.as_view(), name="user_edit_view"),
    path("user-delete/<uuid:id>", UserDeleteView.as_view(), name="user_delete_view"),
    path("user-export/<str:file_type>", UserExportView.as_view(), name="user_export_view"),
]

offers_urls = [
    path("", OffersView.as_view(), name="offers_view"),
    path("redeemed-offers", RedeemedOffersView.as_view(), name="redeemed_offers_view"),
    path("add-offer", AddOffersView.as_view(), name="add_offer_view"),
    path("edit-offer/<uuid:id>", EditOfferView.as_view(), name="edit_offer_view"),
]

prescription_urls = [
    path("", PrescriptionView.as_view(), name="prescription_view"),
    path("detailed-view/<uuid:id>", PrescriptionDetailView.as_view(), name="prescription_detailed_view"),
    path("change-status/<uuid:id>/<str:status>", ChangePrescriptionStatusView.as_view(), name="change_status_view"),
]

notification_urls = [
    path("", NotificationView.as_view(), name="notification_view"),
]


subscription_urls = [
    path("", SubscriptionView.as_view(), name="subscription_view"),
    path("user-subscription-plans", UserSubscriptionView.as_view(), name="user_subscription_plans_view"),
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
