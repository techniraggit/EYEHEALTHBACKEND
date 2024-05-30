from django.urls import path, include
from .views.auth import *
from .views.dashbord import *
from .views.users import *

auth_urls = [
    path("", LoginView.as_view(), name="login_view"),
    path("logout", LogoutView.as_view(), name="logout_view"),
]

dashboard_urls = [
    path("", DashboardView.as_view(), name="dashboard_view"),
]

users_urls = [
    path("", UserView.as_view(), name="users_view"),
]


urlpatterns = [
    path("", include(auth_urls)),
    path("dashboard/", include(dashboard_urls)),
    path("users/", include(users_urls)),
]
