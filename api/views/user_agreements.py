from .base import APIView
from api.models.user_agreements import PrivacyPolicy, TermsAndConditions
from core.utils import api_response


class UserAgreementView(APIView):
    def get(self, request):
        privacy_policy_obj = PrivacyPolicy.objects.all().order_by("-created_on").first()
        term_and_condition_obj = TermsAndConditions.objects.all().order_by("-created_on").first()
        return api_response(
            True,
            200,
            privacy_policy=privacy_policy_obj.to_json() if privacy_policy_obj else {},
            term_and_condition=term_and_condition_obj.to_json() if privacy_policy_obj else {},
        )