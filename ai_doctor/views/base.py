from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated


# Custom mixin for authenticated users.
class UserMixin(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
