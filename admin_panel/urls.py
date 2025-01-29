from django.urls import path, include
from .views import (
    auth,
    home,
    users,
    offers,
    prescription,
    notifications,
    subscription,
    business,
    products,
    eye_test_webhook,
    settings,
    eye_exam,
    trash,
    static_pages,
    credentials,
    my_profile,
    carousels,
)

auth_urls = [
    path("", auth.LoginView.as_view(), name="login_view"),
    path("logout", auth.LogoutView.as_view(), name="logout_view"),
]

home_urls = [
    path("", home.HomeView.as_view(), name="home_view"),
]

users_urls = [
    path("", users.UserView.as_view(), name="users_view"),
    path("user-view/<uuid:id>", users.UserDetailedView.as_view(), name="user_detailed_view"),
    path("user-edit/<uuid:id>", users.UserEditView.as_view(), name="user_edit_view"),
    path("add-user", users.AddUserView.as_view(), name="add_user_view"),
    path("add-admin", users.AddAdminView.as_view(), name="add_admin_view"),
    path("user-delete/<uuid:id>", users.UserDeleteView.as_view(), name="user_delete_view"),
    path("change-user-status/<uuid:id>", users.ChangeUserStatusView.as_view(), name="change_user_status_view"),
    path("user-bulk-delete-view", users.UserBulkDeleteView.as_view(), name="user_bulk_delete_view"),
    path("user-export/<str:file_type>", users.UserExportView.as_view(), name="user_export_view"),
]

offers_urls = [
    path("", offers.OffersView.as_view(), name="offers_view"),
    path("add-offer", offers.AddOffersView.as_view(), name="add_offer_view"),
    path("edit-offer/<uuid:id>", offers.EditOfferView.as_view(), name="edit_offer_view"),
    path("offer-detailed-view/<uuid:id>", offers.OfferDetailedView.as_view(), name="offer_detailed_view"),
    path("delete-offer-view/<uuid:id>", offers.DeleteOfferView.as_view(), name="delete_offer_view"),
    path("offer-dispatch", offers.OfferDispatchView.as_view(), name="offer_dispatch_view"),
    path("offer-email", offers.OfferEmailView.as_view(), name="offer_email_view"),
    path("offer-export/<str:file_type>", offers.OfferExportView.as_view(), name="offer_export_view"),
]

redeemed_offer_urls = [
    path("", offers.RedeemedOffersView.as_view(), name="redeemed_offers_view"),
    path("redeemed-offer-export/<str:file_type>", offers.RedeemedOffersExportView.as_view(), name="redeemed_offer_export_view"),
    path("edit-redeemed-offer-view/<uuid:id>", offers.EditRedeemedOffer.as_view(), name="edit_redeemed_offer_view"),

]

prescription_urls = [
    path("", prescription.PrescriptionView.as_view(), name="prescription_view"),
    path("detailed-view/<uuid:id>", prescription.PrescriptionDetailView.as_view(), name="prescription_detailed_view"),
    path("change-status/<uuid:id>", prescription.ChangePrescriptionStatusView.as_view(), name="change_status_view"),
    path("prescription-export/<str:file_type>", prescription.PrescriptionExportView.as_view(), name="prescription_export_view"),
]

notification_urls = [
    path("my-notification", notifications.MyNotificationView.as_view(), name="my_notification_view"),
    path("mark-this-read", notifications.MarkThisRead.as_view(), name="mark_this_read_view"),
    path("", notifications.NotificationView.as_view(), name="notification_view"),
    path("notification-detailed/<uuid:id>", notifications.NotificationDetailedView.as_view(), name="notification_detailed_view"),
    path("add-notification", notifications.NewNotificationView.as_view(), name="add_notification_view"),
    path("search-users-listing", notifications.UsersSearchListing.as_view(), name="search_users_listing"),
    path("notification-export/<str:file_type>", notifications.NotificationExportView.as_view(), name="notification_export_view"),
]


subscription_urls = [
    path("", subscription.SubscriptionView.as_view(), name="subscription_view"),
    path("detailed-subscription/<uuid:id>", subscription.SubscriptionPlanDetailedView.as_view(), name="detailed_view"),
    path("edit-subscription/<uuid:id>", subscription.SubscriptionEditView.as_view(), name="edit_subscription_view"),
    path("delete-subscription/<uuid:id>", subscription.SubscriptionDeleteView.as_view(), name="delete_subscription_view"),
    path("add-subscription", subscription.SubscriptionAddView.as_view(), name="add_subscription_view"),
    path("subscription-export/<str:file_type>", subscription.SubscriptionExportView.as_view(), name="subscription_export_view"),
]

user_subscriptions_urls = [
        path("user-subscription-plans", subscription.UserSubscriptionView.as_view(), name="user_subscription_plans_view"),
    path("user-subscription-detail/<uuid:id>", subscription.UserSubscriptionDetailView.as_view(), name="user_subscription_detail_view"),
    path("user-subscription-export/<str:file_type>", subscription.UserSubscriptionExportView.as_view(), name="user_subscription_export_view"),
]

settings_urls = [
    path("", settings.SettingsView.as_view(), name="settings_view"),
]

eye_test_urls = [
    path("", eye_exam.EyeTestView.as_view(), name="eye_test_view"),
    path("eye-test-detailed/<uuid:id>", eye_exam.EyeTestDetailedView.as_view(), name="eye_test_view"),
    path("eye-test-export/<str:file_type>", eye_exam.EyeTestExportView.as_view(), name="eye_test_export_view"),
    path("download-eye-test-report/<int:report_id>", eye_exam.DownloadEyeTestReportView.as_view(), name="download_eye_test_report_view"),
]

eye_fatigue_urls = [
    path("", eye_exam.EyeFatigueView.as_view(), name="eye_fatigue_view"),
    path("eye-fatigue-detailed/<uuid:id>", eye_exam.EyeFatigueDetailedView.as_view(), name="eye_fatigue_detailed_view"),
    path("eye-fatigue-export/<str:file_type>", eye_exam.EyeFatigueExportView.as_view(), name="eye_fatigue_export_view"),
]

trash_urls = [
    path("", trash.TrashView.as_view(), name="trash_view"),
    path("restore-user/<uuid:id>", trash.RestoreUserView.as_view(), name="restore_user"),
    path("restore-offer/<uuid:id>", trash.RestoreOfferView.as_view(), name="restore_offer"),
    path("restore-subscription-plan/<uuid:id>", trash.RestoreSubscriptionPlanView.as_view(), name="restore_subscription_plan"),
    path("dlt-user/<uuid:id>", trash.FDeleteUserView.as_view(), name="force_dlt_user_view"),
    path("dlt-offer/<uuid:id>", trash.FDeleteOfferView.as_view(), name="force_dlt_offer_view"),
    path("dlt-subscription-plan/<uuid:id>", trash.FDeleteSubscriptionPlanView.as_view(), name="force_dlt_subscription_plan_view"),
]

credentials_urls = [
    path("", credentials.CredentialsView.as_view(), name="credentials_view"),
    path("add-credential", credentials.AddCredentialsView.as_view(), name="add_credentials_view"),
    path("update-credential/<uuid:id>", credentials.UpdateCredentialsView.as_view(), name="update_credentials_view"),
    path("delete-credential/<uuid:id>", credentials.DeleteCredentialsView.as_view(), name="delete_credentials_view"),
]

profile_urls = [
    path("", my_profile.MyProfileView.as_view(), name="my_profile_view"),
    path("update-profile", my_profile.UpdateProfileView.as_view(), name="update_profile_view"),
]

carousels_urls = [
    path("", carousels.CarouselsView.as_view(), name="carousels_view"),
    path("change-carousel-status/<uuid:id>", carousels.ChangeCarouselStatusView.as_view(), name="carousels_view"),
    path("carousel-detailed-view/<uuid:id>", carousels.CarouselDetailedView.as_view(), name="carousel_detailed_view"),
    path("carousel-export/<str:file_type>", carousels.CarouselExportView.as_view(), name="carousel_export_view"),
    path("delete-carousel-view/<uuid:id>", carousels.DeleteCarouselView.as_view(), name="delete_carousel_view"),
    path("add-carousel-view", carousels.AddCarouselView.as_view(), name="add_carousel_view"),
    path("edit-carousel-view/<uuid:id>", carousels.EditCarouselView.as_view(), name="edit_carousel_view"),
]
static_pages_url = [
    path("", static_pages.StaticPageView.as_view(), name="static_pages_view"),
    path("detailed-view/<uuid:id>", static_pages.StaticPageDetailedView.as_view(), name="detailed_static_page_view"),
    path("add-page", static_pages.AddStaticPageView.as_view(), name="add_static_page_view"),
    path("edit-page/<uuid:id>", static_pages.EditStaticPageView.as_view(), name="edit_static_page_view"),
    path("download-page/<uuid:id>", static_pages.DownloadContentPage.as_view(), name="download_static_page_view"),
]

business_urls = [
    path("business-listing", business.BusinessView.as_view(), name="business_view"),
    path("business-detail-view", business.BusinessDetailView.as_view(), name="business_detail_view"),
    path("add-business", business.BusinessAddView.as_view(), name="business_add_view"),
    path("business-edit/<uuid:business_id>", business.BusinessEditView.as_view(), name="business_edit_view"),
    path("update-business-status", business.UpdateBusinessStatus.as_view(), name="update_business_status_view"),
]

store_urls = [
    path("store/", business.StoreView.as_view(), name="store_view"),
    path("store-with-id/<uuid:store_id>", business.StoreView.as_view(), name="store_view"),
    path("store/<uuid:business_id>", business.BusinessStoreView.as_view(), name="store_with_business"),
    path("add-store", business.AddStoreView.as_view(), name="add_store_view"),
    path("edit-store/<uuid:store_id>", business.EditStoreView.as_view(), name="edit_store_view"),
    path("delete-store/<uuid:store_id>", business.DeleteStoreView.as_view(), name="delete_store_view"),
    path("update-store-status", business.UpdateStoreStatus.as_view(), name="update_store_status_view"),
]

appointment_urls = [
    path("", business.AppointmentView.as_view(), name="appointment_listing_view"),
    path("update-appointment-status", business.UpdateAppointmentStatusView.as_view(), name="update_appointment_status_view"),
    path("appointment-detail/<int:appointment_id>", business.AppointmentDetailView.as_view(), name="appointment_detail_view"),
]

product_urls = [
    path("", products.FramesView.as_view(), name="frame_listing_view"),
    path("frame-details/<int:id>", products.FrameDetailView.as_view(), name="frame_detail_view"),
    path("edit-frame/<int:id>", products.EditFrameView.as_view(), name="edit_frame_view"),
    path("delete-frame/<int:id>", products.DeleteFrameView.as_view(), name="delete_frame_view"),
    path("update-frame-recommendation", products.UpdateFramesRecommendation.as_view(), name="update_frame_recommendation_view"),
    path("add-frame", products.AddFrameView.as_view(), name="add_frame_view"),
]

urlpatterns = [
    path("", include(auth_urls)),
    path("home/", include(home_urls)),
    path("users/", include(users_urls)),
    path("offers/", include(offers_urls)),
    path("redeemed-offers/", include(redeemed_offer_urls)),
    path("prescription/", include(prescription_urls)),
    path("notification/", include(notification_urls)),
    path("subscription/", include(subscription_urls)),
    path("user-subscription/", include(user_subscriptions_urls)),
    path("settings/", include(settings_urls)),
    path("eye-test/", include(eye_test_urls)),
    path("eye-fatigue/", include(eye_fatigue_urls)),
    path("trash/", include(trash_urls)),
    path("static-pages/", include(static_pages_url)),
    path("credentials/", include(credentials_urls)),
    path("my-profile/", include(profile_urls)),
    path("carousels/", include(carousels_urls)),
    path("business/", include(business_urls)),
    path("store/", include(store_urls)),
    path("appointment/", include(appointment_urls)),
    path("products/", include(product_urls)),
    path("eye-test-webhook", eye_test_webhook.InsertEyeTestRecord.as_view()),
]
