import logging
from django.http import JsonResponse
from .base import AdminLoginView
from django.shortcuts import render
from django.core.paginator import Paginator
from store.models import Services


logger = logging.getLogger(__name__)


class BusinessView(AdminLoginView):
    def get(self, request):
        companies = UserModel.objects.filter(is_company=True)
        paginator = Paginator(companies, 10)
        page_number = request.GET.get("page")
        paginated_companies = paginator.get_page(page_number)
        context = dict(
            paginated_companies=paginated_companies,
            is_business=True,
        )
        return render(request, "store/business_listing.html", context)


from api.models.accounts import UserModel
from utilities.utils import is_valid_phone, is_valid_email, generate_password


class BusinessAddView(AdminLoginView):
    def get(self, request):
        return render(
            request,
            "store/business_add.html",
        )

    def post(self, request):
        name = request.POST.get("name")
        email = request.POST.get("email")
        phone_number = request.POST.get("phone_number")
        status = request.POST.get("status", "") == "active"
        if not all([name, email, phone_number]):
            return JsonResponse(
                {"status": False, "message": "Required fields are missing"}
            )

        if is_valid_phone(phone_number):
            return JsonResponse({"status": False, "message": "Invalid phone number"})

        if not is_valid_email(email):
            return JsonResponse({"status": False, "message": "Invalid email"})

        try:
            raw_password = generate_password()
            user_obj = UserModel.objects.create(
                company_name=name,
                is_company=True,
                email=email,
                phone_number=phone_number,
                is_active=status,
            )
            user_obj.set_password(raw_password)
            user_obj.save()

            return JsonResponse(
                {
                    "status": True,
                    "message": "Business added successfully",
                }
            )
        except Exception as e:
            return JsonResponse(
                {
                    "status": False,
                    "message": "Business not added",
                    "error": str(e),
                }
            )


from django.contrib import messages
from django.shortcuts import redirect
from store.models import Stores


class BusinessStoreView(AdminLoginView):
    def get(self, request, business_id):
        try:
            business_obj = UserModel.objects.get(id=business_id, is_company=True)
        except:
            messages.error(request, "Business does not exist")
            return redirect("business_view")
        stores = Stores.objects.filter(company=business_obj)
        context = dict(business_name=business_obj.company_name, stores=stores)
        return render(request, "store/business_store_listing.html", context)


class StoreView(AdminLoginView):
    def get(self, request):
        stores = Stores.objects.all()
        paginator = Paginator(stores, 10)
        page_number = request.GET.get("page")
        paginated_stores = paginator.get_page(page_number)
        context = dict(
            is_store=True,
            paginated_stores=paginated_stores,
        )
        return render(request, "store/store_listing.html", context)


class AddStoreView(AdminLoginView):
    def get(self, request):
        businesses_qs = UserModel.objects.filter(is_company=True)
        services_qs = Services.objects.all()
        context = dict(
            businesses=businesses_qs,
            services=services_qs,
            is_store=True,
        )
        return render(request, "store/add_store.html", context=context)
