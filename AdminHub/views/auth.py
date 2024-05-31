from django.shortcuts import render, redirect

from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth import login, authenticate, logout
from django.views import View

User = get_user_model()


# Create your views here.
class LoginView(View):
    def get(self, request):
        if request.user.is_authenticated and request.user.is_superuser:
            return redirect("home_view")
        return render(request, "auth/login.html")

    def post(self, request):
        email = request.POST.get("email")
        password = request.POST.get("password")

        if not email or not password:
            messages.error(request, "Invalid Login credentials")
            return redirect("login_view")

        try:
            User.objects.get(email=email)
        except:
            messages.error(request, "Such user does not exist")
            return redirect("login_view")

        auth_user = authenticate(request, username=email, password=password)
        if auth_user is not None:
            if not auth_user.is_superuser:
                messages.error(request, "Not a valid user")
                return redirect("login_view")
            login(request, auth_user)
            messages.success(request, "Login successful")
            return redirect("home_view")
        messages.error(request, "Not a valid email address or password")
        return redirect("login_view")


class LogoutView(View):
    def get(self, request):
        logout(request)
        messages.success(request, "Logged out successfully")
        return redirect("login_view")
