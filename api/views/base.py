from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.views import APIView
from rest_framework.permissions import BasePermission


class IsAdminOnly(BasePermission):
    def has_permission(self, request, view):
        if request.user.is_superuser and request.user.is_active:
            return True
        return False


class UserMixin(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]


class AdminMixin(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, IsAdminOnly]
