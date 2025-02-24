from django.urls import path, include
from api.views.accounts import *
from api.views.user_apis import *
from api.views.subscription import *
from api.views.eye_test_apis import *
from api.views import eye_fatigue_apis
from api.views.strip_apis import *
from api.views import static_pages
from api.views import razor_pay_apis
from api.views import blog

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
    path("dashboard-count", Dashboard.as_view()),
    path("user_notification", NotificationView.as_view()),
    path("profile", ProfileView.as_view()),
    path("offers", OffersView.as_view()),
    path("prescription", UserPrescriptionsView.as_view()),
    path("address", UserAddressesView.as_view()),
    path("my-referrals", MyReferralsView.as_view()),
    path("redeemed-offers", UserRedeemedOffersView.as_view()),
    path("contact-upload", UploadUserContactView.as_view()),
    path("delete-account", UserAccountDeleteView.as_view()),
]

strip_urls = [
    path("create-checkout-session", CreateCheckoutSession.as_view()),
    path("webhook", WebHook.as_view()),
    path("create-customer", CreateCustomerView.as_view()),
    path("rzp-webhook", razor_pay_apis.RazorPayWebHook.as_view()),
]

eye_health_apis = [
    path("add-customer", CustomerView.as_view()),
    path("get-question-details", GetQuestionDetails.as_view()),
    path("get-eye-access-token", AccessTokenView.as_view()),
    path("select-questions", SelectQuestion.as_view()),
    path("select-eye", SelectEye.as_view()),
    path("snellen-fraction/", GetSnellenFraction.as_view()),
    path("random-text", RandomText.as_view()),
    path("myopia-or-hyperopia-or-presbyopia-test", MyopiaOrHyperopiaOrPresbyopiaTest.as_view()),
    path("choose-astigmatism", ChooseAstigmatism.as_view()),
    path("get-degrees", GetDegrees.as_view()),
    path("choose-degree-api", ChooseDegreeApi.as_view()),
    path("cyl-test", CylTest.as_view()),
    path("snellen-fraction-red-green-test", GetSnellenFractionRedGreenTest.as_view()),
    path("final-red-green-action-test", FinalRedGreenActionTest.as_view()),
    path("update-red-green-action-api", UpdateRedGreenActionApi.as_view()),
    path("random-word-test", RandomWordTest.as_view()),
    path("update-Reading-SnellenFraction-TestApi", UpdateReadingSnellenFractionTestApi.as_view()),
    path("generate-report", GetGeneratedReport.as_view()),
    path("calculate-distance", CalculateDistance.as_view()),
    path("reports", EyeTestReports.as_view()),
    path("download-reports", DownloadReportView.as_view()),
    path("counter-api", CounterApiView.as_view()),
    path("reading-snellen-fraction", ReadingSnellenFractionView.as_view()),
    path("random-word-Reading-test", RandomWordReadingTestView.as_view()),
]

fatigue_apis = [
    path("add-customer", eye_fatigue_apis.AddCustomer.as_view()),
    path("calculate-blink-rate", eye_fatigue_apis.CalculateBlinkRate.as_view()),
    path("blinks-report-details", eye_fatigue_apis.BlinkReportDetails.as_view()),
    path("fatigue-reports", eye_fatigue_apis.EyeFatigueReportsView.as_view()),
    path("fatigue-graph", eye_fatigue_apis.EyeFatigueGraph.as_view()),
    path("download-report", eye_fatigue_apis.DownloadReportView.as_view()),
    path("take-user-selfie", eye_fatigue_apis.TakeUserSelfie.as_view()),
]

static_page_urls = [
    path("page/<slug:slug>", static_pages.StaticPagesView.as_view()),
    path("page", static_pages.StaticPagesSlugView.as_view()),
]

blog_urls = [
    path("", blog.BlogListingView.as_view(), name="blog_view"),
    path("blog-detail/<uuid:blog_id>", blog.BlogDetailView.as_view(), name="blog_detail_view"),
]

urlpatterns = (
    accounts
    + subscriptions
    + users
    + [
        path("eye/", include(eye_health_apis)),
        path("payment/", include(strip_urls)),
        path("fatigue/", include(fatigue_apis)),
        path("static/", include(static_page_urls)),
        path("blog/", include(blog_urls)),
        
    ]
)
