from django.urls import path, include
from .views import apis

api_urls = [
    path("ask", apis.AskDoctorView.as_view()),
    path("prompts", apis.PredefinedPromptsView.as_view()),
    path("consent-accept", apis.UserConsentAcceptView.as_view()),
]

urlpatterns = [
    path("api/", include(api_urls)),
]
