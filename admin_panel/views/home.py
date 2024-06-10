from .base import AdminLoginView
from django.shortcuts import render
from api.models.accounts import UserModel
from api.models.rewards import Offers, UserRedeemedOffers
from api.models.prescription import UserPrescriptions
from api.models.eye_health import EyeFatigueReport, EyeTestReport


class HomeView(AdminLoginView):
    def get(self, request):
        # Models Query Set
        user_queryset = UserModel.objects.all()
        offers_queryset = Offers.objects.all()
        redeemed_offers_queryset = UserRedeemedOffers.objects.all()
        prescriptions_queryset = UserPrescriptions.objects.all()
        eye_fatigue_queryset = EyeFatigueReport.objects.all()
        eye_test_queryset = EyeTestReport.objects.all()

        # Counts
        total_users = user_queryset.exclude(is_superuser=True).count()
        total_offers = offers_queryset.count()
        total_redeemed_offers = redeemed_offers_queryset.exclude(status="pending").count()
        total_prescriptions = prescriptions_queryset.filter(status="approved").count()
        total_eye_tests = eye_fatigue_queryset.count()
        total_eye_fatigue_test = eye_test_queryset.count()
        context = dict(
            is_home=True,
            total_users=total_users,
            total_offers=total_offers,
            total_redeemed_offers=total_redeemed_offers,
            total_prescriptions=total_prescriptions,
            total_eye_tests=total_eye_tests,
            total_eye_fatigue_test=total_eye_fatigue_test,
        )
        return render(request, "home/home.html", context)
