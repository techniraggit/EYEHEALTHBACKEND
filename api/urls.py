from django.urls import path, include
from api.views.accounts import *
from api.views.user_apis import *
from api.views.subscription import *
from api.views.eye_test_apis import *
from api.views import eye_fatigue_apis
from api.views.strip_apis import *

accounts = [
    path("verification_otp", VerificationOTPView.as_view()),
    path("register", RegisterView.as_view()),
    path("send_login_otp", SendLoginOTP.as_view()),
    path("verify_login_otp", VerifyLoginOTPView.as_view()),
    path("validate_referral_code", ValidateReferralCode.as_view()),
    path("is_already_verified", IsAlreadyVerified.as_view()),
]

subscriptions = [
    path("subscription-plans", SubscriptionPlansView.as_view()),
    path("is-active-plan", IsActivePlan.as_view()),
]

users = [
    path("user_notification", NotificationView.as_view()),
    path("profile", ProfileView.as_view()),
    path("offers", OffersView.as_view()),
    path("prescription", UserPrescriptionsView.as_view()),
    path("address", UserAddressesView.as_view()),
]

strip_urls = [
    path("create-checkout-session", CreateCheckoutSession.as_view()),
    path("webhook", WebHook.as_view()),  # localhost:8000api/payment/webhook
    path("create-customer", CreateCustomerView.as_view()),
]

eye_health_apis = [
    path("add-customer", CustomerView.as_view()),
    path("get-question-details", GetQuestionDetails.as_view()),
    path("get-eye-access-token", AccessTokenView.as_view()),
    path("select-questions", SelectQuestion.as_view()),
    path("select-eye", SelectEye.as_view()),
    path("snellen-fraction/", GetSnellenFraction.as_view()),
    path("random-text", RandomText.as_view()),
    path(
        "myopia-or-hyperopia-or-presbyopia-test",
        MyopiaOrHyperopiaOrPresbyopiaTest.as_view(),
    ),
    path("choose-astigmatism", ChooseAstigmatism.as_view()),
    path("get-degrees", GetDegrees.as_view()),
    path("choose-degree-api", ChooseDegreeApi.as_view()),
    path("cyl-test", CylTest.as_view()),
    path("snellen-fraction-red-green-test", GetSnellenFractionRedGreenTest.as_view()),
    path("final-red-green-action-test", FinalRedGreenActionTest.as_view()),
    path("update-red-green-action-api", UpdateRedGreenActionApi.as_view()),
    path("random-word-test", RandomWordTest.as_view()),
    path(
        "update-Reading-SnellenFraction-TestApi",
        UpdateReadingSnellenFractionTestApi.as_view(),
    ),
    path("generate-report", GetGeneratedReport.as_view()),
    path("calculate-distance", CalculateDistance.as_view()),
]

fatigue_apis = [
    path("add-customer", eye_fatigue_apis.AddCustomer.as_view()),
    path("calculate-blink-rate", eye_fatigue_apis.CalculateBlinkRate.as_view()),
    path("blinks-report-details", eye_fatigue_apis.BlinkReportDetails.as_view()),
]

urlpatterns = (
    accounts
    + subscriptions
    + users
    + [
        path("eye/", include(eye_health_apis)),
        path("payment/", include(strip_urls)),
        path("fatigue/", include(fatigue_apis)),
    ]
)
