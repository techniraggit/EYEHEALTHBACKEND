from django.urls import path, include
from .views.auth import *
from .views.home import *
from .views.users import *
from .views.offers import *
from .views.prescription import *
from .views.notifications import *
from .views.subscription import *
from .views import settings
from .views import eye_exam
from .views import trash

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
    path("add-user", AddUserView.as_view(), name="add_user_view"),
    path("user-delete/<uuid:id>", UserDeleteView.as_view(), name="user_delete_view"),
    path("user-bulk-delete-view", UserBulkDeleteView.as_view(), name="user_bulk_delete_view"),
    path("user-export/<str:file_type>", UserExportView.as_view(), name="user_export_view"),
]

offers_urls = [
    path("", OffersView.as_view(), name="offers_view"),
    path("redeemed-offers", RedeemedOffersView.as_view(), name="redeemed_offers_view"),
    path("add-offer", AddOffersView.as_view(), name="add_offer_view"),
    path("edit-offer/<uuid:id>", EditOfferView.as_view(), name="edit_offer_view"),
    path("offer-detailed-view/<uuid:id>", OfferDetailedView.as_view(), name="offer_detailed_view"),
    path("delete-offer-view/<uuid:id>", DeleteOfferView.as_view(), name="delete_offer_view"),
    path("edit-redeemed-offer-view/<uuid:id>", EditRedeemedOffer.as_view(), name="edit_redeemed_offer_view"),
    path("offer-dispatch", OfferDispatchView.as_view(), name="offer_dispatch_view"),
    path("offer-email", OfferEmailView.as_view(), name="offer_email_view"),
    path("offer-export/<str:file_type>", OfferExportView.as_view(), name="offer_export_view"),
]

prescription_urls = [
    path("", PrescriptionView.as_view(), name="prescription_view"),
    path("detailed-view/<uuid:id>", PrescriptionDetailView.as_view(), name="prescription_detailed_view"),
    path("change-status/<uuid:id>", ChangePrescriptionStatusView.as_view(), name="change_status_view"),
]

notification_urls = [
    path("", NotificationView.as_view(), name="notification_view"),
    path("notification-detailed/<uuid:id>", NotificationDetailedView.as_view(), name="notification_detailed_view"),
    path("add-notificatioin", NewNotificationView.as_view(), name="add_notification_view"),
]


subscription_urls = [
    path("", SubscriptionView.as_view(), name="subscription_view"),
    path("detailed-subscription/<uuid:id>", SubscriptionPlanDetailedView.as_view(), name="detailed_view"),
    path("edit-subscription/<uuid:id>", SubscriptionEditView.as_view(), name="edit_subscription_view"),
    path("delete-subscription/<uuid:id>", SubscriptionDeleteView.as_view(), name="delete_subscription_view"),
    path("add-subscription", SubscriptionAddView.as_view(), name="add_subscription_view"),
    path("user-subscription-plans", UserSubscriptionView.as_view(), name="user_subscription_plans_view"),
    path("subscription-export/<str:file_type>", SubscriptionExportView.as_view(), name="subscription_export_view"),
    path("user-subscription-export/<str:file_type>", UserSubscriptionExportView.as_view(), name="user_subscription_export_view"),
]

settings_urls = [
    path("", settings.SettingsView.as_view(), name="settings_view"),
]

eye_exam_urls = [
    path("eye-test", eye_exam.EyeTestView.as_view(), name="eye_test_view"),
    path("eye-test-detailed/<uuid:id>", eye_exam.EyeTestDetailedView.as_view(), name="eye_test_view"),
    path("eye-test-export/<str:file_type>", eye_exam.EyeTestExportView.as_view(), name="eye_test_export_view"),
    path("download-eye-test-report/<int:report_id>", eye_exam.DownloadEyeTestReportView.as_view(), name="download_eye_test_report_view"),
    path("eye-fatigue", eye_exam.EyeFatigueView.as_view(), name="eye_fatigue_view"),
    path("eye-fatigue-detailed/<uuid:id>", eye_exam.EyeFatigueDetailedView.as_view(), name="eye_fatigue_detailed_view"),
    path("eye-fatigue-export/<str:file_type>", eye_exam.EyeFatigueExportView.as_view(), name="eye_fatigue_export_view"),
]

trash_urls = [
    path("", trash.TrashView.as_view(), name="trash_view"),
    path("restore-user/<uuid:id>", trash.RestoreUserView.as_view(), name="restore_user"),
    path("restore-offer/<uuid:id>", trash.RestoreOfferView.as_view(), name="restore_offer"),
    path("restore-subscription-plan/<uuid:id>", trash.RestoreSubscriptionPlanView.as_view(), name="restore_subscription_plan"),
]

urlpatterns = [
    path("", include(auth_urls)),
    path("home/", include(home_urls)),
    path("users/", include(users_urls)),
    path("offers/", include(offers_urls)),
    path("prescription/", include(prescription_urls)),
    path("notification/", include(notification_urls)),
    path("subscription/", include(subscription_urls)),
    path("settings/", include(settings_urls)),
    path("eye/", include(eye_exam_urls)),
    path("trash/", include(trash_urls)),
]
