from django.urls import path, include
from .views import apis

api_urls = [
    path("ask", apis.AskDoctorView.as_view()),
]

urlpatterns = [
    path("api/", include(api_urls)),
]
