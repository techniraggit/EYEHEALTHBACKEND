from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from .base import AdminLoginView
from api.models.user_agreements import PrivacyPolicy, TermsAndConditions


class PrivacyPolicyView(AdminLoginView):
    def get(self, request):
        search = request.GET.get("search", "").strip()
        privacy_policies = (
            PrivacyPolicy.objects.filter(title__icontains=search)
            if search
            else PrivacyPolicy.objects.all()
        )
        privacy_policies = privacy_policies.order_by("-created_on")
        paginator = Paginator(privacy_policies, 10)
        page_number = request.GET.get("page")
        paginated_privacy_policies = paginator.get_page(page_number)

        context = {
            "privacy_policies": paginated_privacy_policies,
            "is_privacy_policy": True,
            "search": search,
        }
        return render(request, "privacy_polity/privacy_policy.html", context)


class PrivacyPolicyDetailedView(AdminLoginView):
    def get(self, request, id):
        try:
            privacy_policy_obj = PrivacyPolicy.objects.get(pk=id)
        except PrivacyPolicy.DoesNotExist:
            messages.error(request, "Privacy Policy does not exist")
            return redirect("privacy_policy_list")

        context = {
            "privacy_policy_obj": privacy_policy_obj,
            "is_privacy_policy": True,
        }
        return render(request, "privacy_polity/view_privacy_policy.html", context)


class EditPrivacyPolicyView(AdminLoginView):
    def get(self, request, id):
        try:
            privacy_policy_obj = PrivacyPolicy.objects.get(pk=id)
        except PrivacyPolicy.DoesNotExist:
            messages.error(request, "Privacy Policy does not exist")
            return redirect("privacy_policy_list")

        context = {
            "privacy_policy_obj": privacy_policy_obj,
            "is_privacy_policy": True,
        }
        return render(request, "privacy_polity/edit_privacy_policy.html", context)

    def post(self, request, id):
        policy_content = request.POST.get("policy_content")

        if not policy_content:
            return JsonResponse(
                {"status": False, "message": "Required fields are missing"}
            )

        try:
            privacy_policy_obj = PrivacyPolicy.objects.get(pk=id)
        except PrivacyPolicy.DoesNotExist:
            return JsonResponse(
                {"status": False, "message": "Privacy Policy does not exist"}
            )

        privacy_policy_obj.pk = None
        privacy_policy_obj.content = policy_content
        privacy_policy_obj.save()
        return JsonResponse(
            {"status": True, "message": "Privacy Policy updated successfully"}
        )


class AddPrivacyPolicyView(AdminLoginView):
    def get(self, request):
        context = {"is_privacy_policy": True}
        return render(request, "privacy_polity/add_privacy_policy.html", context)

    def post(self, request):
        policy_content = request.POST.get("policy_content")

        if not policy_content:
            return JsonResponse(
                {"status": False, "message": "Required fields are missing"}
            )

        PrivacyPolicy.objects.create(content=policy_content, created_by=request.user)
        return JsonResponse(
            {"status": True, "message": "Privacy Policy created successfully"}
        )


class TermsAndConditionsView(AdminLoginView):
    def get(self, request):
        search = request.GET.get("search", "").strip()
        term_and_conditions = (
            TermsAndConditions.objects.filter(title__icontains=search)
            if search
            else TermsAndConditions.objects.all()
        )
        term_and_conditions = term_and_conditions.order_by("-created_on")
        paginator = Paginator(term_and_conditions, 10)
        page_number = request.GET.get("page")
        paginated_term_and_conditions = paginator.get_page(page_number)

        context = {
            "term_and_conditions": paginated_term_and_conditions,
            "is_term_and_conditions": True,
            "search": search,
        }
        return render(request, "term_and_conditions/term_and_conditions.html", context)


class TermsAndConditionsDetailedView(AdminLoginView):
    def get(self, request, id):
        try:
            term_and_condition_obj = TermsAndConditions.objects.get(pk=id)
        except TermsAndConditions.DoesNotExist:
            messages.error(request, "Terms and Conditions does not exist")
            return redirect("terms_and_conditions_list")

        context = {
            "term_and_condition_obj": term_and_condition_obj,
            "is_term_and_conditions": True,
        }
        return render(
            request, "term_and_conditions/view_term_and_conditions.html", context
        )


class EditTermsAndConditionsView(AdminLoginView):
    def get(self, request, id):
        try:
            term_and_conditions_obj = TermsAndConditions.objects.get(pk=id)
        except TermsAndConditions.DoesNotExist:
            messages.error(request, "Terms and Conditions does not exist")
            return redirect("terms_and_conditions_list")

        context = {
            "term_and_conditions_obj": term_and_conditions_obj,
            "is_term_and_conditions": True,
        }
        return render(
            request, "term_and_conditions/edit_term_and_conditions.html", context
        )

    def post(self, request, id):
        policy_content = request.POST.get("policy_content")

        if not policy_content:
            return JsonResponse(
                {"status": False, "message": "Required fields are missing"}
            )

        try:
            term_and_condition_obj = TermsAndConditions.objects.get(pk=id)
        except TermsAndConditions.DoesNotExist:
            return JsonResponse(
                {"status": False, "message": "Terms and Conditions does not exist"}
            )

        term_and_condition_obj.pk = None
        term_and_condition_obj.content = policy_content
        term_and_condition_obj.save()
        return JsonResponse(
            {"status": True, "message": "Terms and Conditions updated successfully"}
        )


class AddTermsAndConditionsView(AdminLoginView):
    def get(self, request):
        context = {"is_term_and_conditions": True}
        return render(
            request, "term_and_conditions/add_term_and_conditions.html", context
        )

    def post(self, request):
        term_content = request.POST.get("term_content")

        if not term_content:
            return JsonResponse(
                {"status": False, "message": "Required fields are missing"}
            )

        TermsAndConditions.objects.create(content=term_content, created_by=request.user)
        return JsonResponse(
            {"status": True, "message": "Terms and Conditions created successfully"}
        )
