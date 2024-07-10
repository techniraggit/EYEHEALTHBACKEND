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

        # Counting starts here >>>>>>>>>>
        # Users
        total_users = user_queryset.exclude(is_superuser=True).count()

        # Offers
        total_active_offers = offers_queryset.filter(status="active").count()
        total_inactive_offers = offers_queryset.filter(status="inactive").count()
        total_expired_offers = offers_queryset.filter(status="expired").count()

        # Redeemed Offers
        pending_total_redeemed_offers = redeemed_offers_queryset.filter(status="pending").count()
        approved_total_redeemed_offers = redeemed_offers_queryset.filter(status="approved").count()
        rejected_total_redeemed_offers = redeemed_offers_queryset.filter(status="rejected").count()
        
        # Prescription 
        total_approved_prescriptions = prescriptions_queryset.filter(status="approved").count()
        total_pending_prescriptions = prescriptions_queryset.filter(status="pending").count()
        total_rejected_prescriptions = prescriptions_queryset.filter(status="rejected").count()
        
        # Eye Test
        total_eye_tests = eye_fatigue_queryset.count()
        
        # Eye Fatigue
        total_eye_fatigue_test = eye_test_queryset.count()

        context = dict(
            is_home = True,
            total_users = total_users,
            total_active_offers = total_active_offers,
            total_inactive_offers = total_inactive_offers,
            total_expired_offers = total_expired_offers,
            pending_total_redeemed_offers = pending_total_redeemed_offers,
            approved_total_redeemed_offers = approved_total_redeemed_offers,
            rejected_total_redeemed_offers = rejected_total_redeemed_offers,
            total_approved_prescriptions = total_approved_prescriptions,
            total_pending_prescriptions = total_pending_prescriptions,
            total_rejected_prescriptions = total_rejected_prescriptions,
            total_eye_tests = total_eye_tests,
            total_eye_fatigue_test = total_eye_fatigue_test,
        )
        return render(request, "home/home.html", context)
