from .base import AdminLoginView
from django.shortcuts import render
from api.models.accounts import UserModel
from django.http import JsonResponse


class MyProfileView(AdminLoginView):
    def get(self, request):
        return render(request, "my_profile/my_profile.html")

class UpdateProfileView(AdminLoginView):
    def post(self, request):
        try:
            user_obj = UserModel.objects.get(id=request.user.id)
            user_obj.first_name = request.POST.get("first_name")
            user_obj.last_name = request.POST.get("last_name")
            user_obj.dob = request.POST.get("dob")
            if request.FILES.get("image"):
                user_obj.image = request.FILES.get("image")
            user_obj.save()
            return JsonResponse({
                "status": True,
                "message": "Profile updated successfully"
            })
        except Exception as e:
            return JsonResponse({
                "status": False,
                "message": str(e)
            })