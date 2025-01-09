from django.template.loader import render_to_string
from utilities.services.email import send_email
from django.core.paginator import Paginator
from django.shortcuts import render
from .base import AdminLoginView
from django.http import JsonResponse
import logging
from admin_panel.forms.stores import BusinessModelForm, StoreForm
from utilities.utils import generate_password
from django.contrib.auth.hashers import make_password
from django.contrib import messages
from django.shortcuts import redirect
from store.models import Stores, BusinessModel, Services, StoreImages
from django.core.exceptions import ValidationError
from utilities.utils import get_form_error_msg

logger = logging.getLogger(__name__)


class BusinessView(AdminLoginView):
    def get(self, request):
        companies = BusinessModel.objects.all()
        paginator = Paginator(companies, 10)
        page_number = request.GET.get("page")
        paginated_companies = paginator.get_page(page_number)
        context = dict(
            paginated_companies=paginated_companies,
            is_business=True,
        )
        return render(request, "store/business_listing.html", context)


class BusinessAddView(AdminLoginView):
    def get(self, request):
        return render(
            request,
            "store/business_add.html",
        )

    def post(self, request):
        status = request.POST.get("status", "") == "active"
        form = BusinessModelForm(request.POST)
        if form.is_valid():
            instance = form.save(commit=False)
            password = generate_password()
            instance.password = make_password(password)
            instance.is_active = status
            instance.save()
            # send welcome email to new business
            email_body = render_to_string(
                "email/send_password.html",
                {"name": instance.name, "password": password},
            )
            send_email(
                subject="Welcome to EyeCare",
                message=email_body,
                recipients=[instance.email],
            )

            return JsonResponse(
                {
                    "status": True,
                    "message": "Business added successfully",
                }
            )
        else:
            return JsonResponse(
                {"status": False, "message": get_form_error_msg(form.errors.as_json())}
            )


class BusinessStoreView(AdminLoginView):
    def get(self, request, business_id):
        try:
            business_obj = BusinessModel.objects.get(id=business_id)
        except:
            messages.error(request, "Business does not exist")
            return redirect("business_view")
        stores = Stores.objects.filter(business=business_obj)
        context = dict(business_name=business_obj.name, stores=stores)
        return render(request, "store/business_store_listing.html", context)


class StoreView(AdminLoginView):
    def get(self, request, store_id=None):
        if store_id:
            try:
                store = Stores.objects.get(id=store_id)
                store_images = [
                    f"{request.build_absolute_uri(i.image.url)}"
                    for i in store.images.all()
                ]
                return JsonResponse(
                    {
                        "status": True,
                        "data": store.to_json(),
                        "images": store_images,
                    }
                )
            except Stores.DoesNotExist:
                return JsonResponse(
                    {
                        "status": False,
                        "message": "Store does not exist",
                    }
                )
            except Exception as e:
                return JsonResponse(
                    {
                        "status": False,
                        "message": "An error occurred",
                        "error": str(e),
                    }
                )

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
        businesses_qs = BusinessModel.objects.all()
        services_qs = Services.objects.all()
        context = dict(
            businesses=businesses_qs,
            services=services_qs,
            is_store=True,
        )
        return render(request, "store/add_store.html", context=context)

    def post(self, request):
        services_lst = request.POST.getlist("service")
        images = request.FILES.getlist("images[]")
        form = StoreForm(request.POST, request.FILES)

        if form.is_valid():
            instance = form.save()
            services_qs = Services.objects.filter(id__in=services_lst)
            if services_qs.exists():
                instance.services.add(
                    *services_qs
                )  # Add services to the store instance
            else:
                return JsonResponse(
                    {
                        "status": False,
                        "message": "Some of the selected services are invalid.",
                    }
                )

            try:
                store_images = [StoreImages(store=instance, image=i) for i in images]
                if store_images:
                    StoreImages.objects.bulk_create(store_images)
                return JsonResponse(
                    {
                        "status": True,
                        "message": "Store added successfully",
                    }
                )

            except ValidationError as e:
                return JsonResponse(
                    {
                        "status": False,
                        "message": f"Error occurred while saving the store: {str(e)}",
                    }
                )
        return JsonResponse(
            {
                "status": False,
                "message": get_form_error_msg(form.errors.as_json()),
            }
        )


class EditStoreView(AdminLoginView):
    def get(self, request, store_id):
        try:
            # Retrieve the store instance by ID
            store_instance = Stores.objects.get(id=store_id)
        except Stores.DoesNotExist:
            return JsonResponse({"status": False, "message": "Store not found."})

        # Fetch related businesses and services for the dropdowns
        businesses_qs = BusinessModel.objects.all()
        services_qs = Services.objects.all()

        # Prepare context for rendering the edit form
        store_images = [
            f"{request.build_absolute_uri(i.image.url)}"
            for i in store_instance.images.all()
        ]
        context = dict(
            store=store_instance,
            businesses=businesses_qs,
            services=services_qs,
            service_ids=store_instance.services.all().values_list("id", flat=True),
            store_images=store_images,
            is_store=True,
        )
        return render(request, "store/store_edit.html", context=context)

    def post(self, request, store_id):
        try:
            # Retrieve the store instance to update
            store_instance = Stores.objects.get(id=store_id)
        except Stores.DoesNotExist:
            return JsonResponse({"status": False, "message": "Store not found."})

        # Get updated data from the form
        services_lst = request.POST.getlist("service")
        images = request.FILES.getlist("images[]")
        form = StoreForm(request.POST, request.FILES, instance=store_instance)

        if form.is_valid():
            # Update the store instance
            instance = form.save()

            # Update the services related to the store
            services_qs = Services.objects.filter(id__in=services_lst)
            if services_qs.exists():
                instance.services.set(services_qs)  # Update related services
            else:
                return JsonResponse(
                    {
                        "status": False,
                        "message": "Some of the selected services are invalid.",
                    }
                )

            try:
                # Update images by clearing old ones and adding new ones
                if images:
                    StoreImages.objects.filter(store=instance).delete()
                    store_images = [
                        StoreImages(store=instance, image=i) for i in images
                    ]
                    StoreImages.objects.bulk_create(store_images)

                return JsonResponse(
                    {
                        "status": True,
                        "message": "Store updated successfully",
                    }
                )

            except ValidationError as e:
                return JsonResponse(
                    {
                        "status": False,
                        "message": f"Error occurred while updating the store: {str(e)}",
                    }
                )

        # If the form is invalid, return the error messages
        return JsonResponse(
            {
                "status": False,
                "message": get_form_error_msg(form.errors.as_json()),
            }
        )


class DeleteStoreView(AdminLoginView):
    def get(self, request, store_id):
        try:
            # Retrieve the store instance to delete
            store_instance = Stores.objects.get(id=store_id)
        except Stores.DoesNotExist:
            return JsonResponse({"status": False, "message": "Store not found."})

        # Delete the store instance
        store_instance.delete()

        return JsonResponse({"status": True, "message": "Store deleted successfully."})
