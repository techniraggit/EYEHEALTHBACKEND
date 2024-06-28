from .base import AdminLoginView
from django.shortcuts import render


class MyProfileView(AdminLoginView):
    def get(self, request):
        return render(request, "my_profile/my_profile.html")