from .base import AdminLoginView
from django.shortcuts import render
from django.http import JsonResponse
from api.models.dashboard import CarouselModel
from django.core.paginator import Paginator
from core.constants import ERROR_500_MSG
from django.db.models import Q
from datetime import datetime


class CarouselsView(AdminLoginView):
    def get(self, request):
        carousels_qs = CarouselModel.objects.all().order_by("-created_on")
        search = request.GET.get("search", "").strip()
        start_date_filter = request.GET.get("start_date_filter")
        end_date_filter = request.GET.get("end_date_filter")
        carousel_status_filter = request.GET.get("carousel_status_filter")
        
        if search:
            carousels_qs = carousels_qs.filter(
                Q(name__icontains=search)
            )
        
        if start_date_filter and not end_date_filter:
            start_date_filter = datetime.strptime(start_date_filter, "%Y-%m-%d").date()
            carousels_qs = carousels_qs.filter(created_on__gte=start_date_filter)
        
        if end_date_filter and not start_date_filter:
            end_date_filter = datetime.strptime(end_date_filter, "%Y-%m-%d").date()
            carousels_qs = carousels_qs.filter(created_on__lte=end_date_filter)
        
        if start_date_filter and end_date_filter:
            start_date_filter = datetime.strptime(start_date_filter, "%Y-%m-%d").date()
            end_date_filter = datetime.strptime(end_date_filter, "%Y-%m-%d").date()
            carousels_qs = carousels_qs.filter(
                created_on__date__range=(start_date_filter, end_date_filter)
            )
        
        if carousel_status_filter:
            carousels_qs = carousels_qs.filter(is_active=carousel_status_filter=="active")


        paginator = Paginator(carousels_qs, 10)
        page_number = request.GET.get("page")
        paginated_carousels = paginator.get_page(page_number)

        context = dict(
            is_carousel=True,
            paginated_carousels=paginated_carousels,
            search = search,
            start_date_filter = start_date_filter,
            end_date_filter = end_date_filter,
            carousel_status_filter = carousel_status_filter,
        )
        return render(request, "carousel/listing.html", context)

from admin_panel.forms.carousels import CarouselModelForm
from utilities.utils import get_form_error_msg
class AddCarouselView(AdminLoginView):
    def get(self, request):
        context = dict(
            is_carousel=True
        )
        return render(request, "carousel/add.html", context=context)
    
    def post(self, request):
        carousel_form = CarouselModelForm(data=request.POST, files=request.FILES)
        if carousel_form.is_valid():
            carousel_form.save()
            return JsonResponse(
                {
                    "status": True,
                    "message": "Carousel added successfully",
                }
            )
        errors = carousel_form.errors.as_json()
        message = get_form_error_msg(errors)
        return JsonResponse({
            "status": False,
            "message": message,
        })
    
from django.contrib import messages
from django.shortcuts import redirect

class EditCarouselView(AdminLoginView):
    def get(self, request, id):
        try:
            carousel_obj = CarouselModel.objects.get(id=id)
        except:
            messages.error(request, "Carousel does not exist")
            return redirect("carousels_view")
        context = dict(
            is_carousel=True,
            carousel_obj=carousel_obj,
        )
        return render(request, "carousel/edit.html", context=context)
    
    def post(self, request, id):
        try:
            carousel_obj = CarouselModel.objects.get(id=id)
        except:
            return JsonResponse(
                {
                    "status": False,
                    "message": "Carousel does not exist",
                }
            )
        try:
            carousel_obj.name = request.POST.get("name")
            carousel_obj.is_active = request.POST.get("status", "").lower() == "active"
            if request.FILES.get("image"):
                carousel_obj.image = request.FILES.get("image")
            carousel_obj.save()
            return JsonResponse(
                {
                    "status": True,
                    "message": "Carousel updated successfully",
                }
            )

        except Exception as e:
            return JsonResponse({
                "status": False,
                "message": str(e),
            })

class CarouselDetailedView(AdminLoginView):
    def get(self, request, id):
        try:
            carousel_obj = CarouselModel.objects.get(id=id)
        except:
            return JsonResponse(
                {
                    "status": False,
                    "message": "Carousel does not exist",
                }
            )
        return JsonResponse(
            {
                "status": True,
                "carousel": carousel_obj.to_json(request=request),
            }
        )

class ChangeCarouselStatusView(AdminLoginView):
    def get(self, request, id):
        try:
            carousel_obj = CarouselModel.objects.get(id=id)
        except:
            return JsonResponse(
                {
                    "status": False,
                    "message": "Carousel does not exist",
                }
            )

        try:
            carousel_obj.is_active = not carousel_obj.is_active
            carousel_obj.save()
            message = "Activated" if carousel_obj.is_active else "Inactivated"
            return JsonResponse(
                {
                    "status": True,
                    "carousel_current_status": carousel_obj.is_active,
                    "message": f"Carousel {message} successfully",
                }
            )
        except Exception as e:
            return JsonResponse(
                {
                    "status": False,
                    "message": ERROR_500_MSG,
                    "error": str(e),
                }
            )

class DeleteCarouselView(AdminLoginView):
    def get(self, request, id):
        try:
            carousel_obj = CarouselModel.objects.get(id=id)
        except:
            return JsonResponse(
                {
                    "status": False,
                    "message": "Carousel does not exist",
                }
            )

        try:
            carousel_obj.delete()
            return JsonResponse(
                {
                    "status": True,
                    "message": f"Carousel deleted successfully",
                }
            )
        except Exception as e:
            return JsonResponse(
                {
                    "status": False,
                    "message": ERROR_500_MSG,
                    "error": str(e),
                }
            )

from django.http import HttpResponse
from utilities.utils import time_localize
import csv
from openpyxl import Workbook
from openpyxl.writer.excel import save_virtual_workbook

class CarouselExportView(AdminLoginView):
    def get(self, request, file_type):
        if file_type == "csv":
            return self.csv_export(request)
        elif file_type == "excel":
            return self.excel_export(request)
        else:
            return HttpResponse("Invalid file type")

    def get_file_name(self):
        current_timestamp = time_localize(datetime.now()).strftime("%Y%m%d%H%M%S")
        return f"carousels-{current_timestamp}"

    def get_queryset(self, request):
        search = request.GET.get("search", "").strip()
        start_date_filter = request.GET.get("start_date_filter")
        end_date_filter = request.GET.get("end_date_filter")
        carousel_status_filter = request.GET.get("carousel_status_filter")

        carousels_qs = CarouselModel.objects.all().order_by("-created_on")
        
        if search:
            carousels_qs = carousels_qs.filter(
                Q(name__icontains=search)
            )
        
        if start_date_filter and not end_date_filter:
            start_date_filter = datetime.strptime(start_date_filter, "%Y-%m-%d").date()
            carousels_qs = carousels_qs.filter(created_on__gte=start_date_filter)
        
        if end_date_filter and not start_date_filter:
            end_date_filter = datetime.strptime(end_date_filter, "%Y-%m-%d").date()
            carousels_qs = carousels_qs.filter(created_on__lte=end_date_filter)
        
        if start_date_filter and end_date_filter:
            start_date_filter = datetime.strptime(start_date_filter, "%Y-%m-%d").date()
            end_date_filter = datetime.strptime(end_date_filter, "%Y-%m-%d").date()
            carousels_qs = carousels_qs.filter(
                created_on__date__range=(start_date_filter, end_date_filter)
            )
        
        if carousel_status_filter:
            carousels_qs = carousels_qs.filter(is_active=carousel_status_filter=="active")

        return carousels_qs

    def get_headers(self):
        return [
            "ID",
            "Name",
            "Image",
            "Status",
            "Created At",
        ]

    def get_data_row(self, object, request):
        return [
            str(object.pk),
            object.name,
            request.build_absolute_uri(object.image.url) if object.image else "",
            "Active" if object.is_active else "Inactive",
            time_localize(object.created_on).strftime('%Y-%m-%d, %I:%M %p'),
        ]

    def csv_export(self, request):
        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = (
            f'attachment; filename="{self.get_file_name()}.csv"'
        )
        writer = csv.writer(response)
        writer.writerow(self.get_headers())
        for user in self.get_queryset(request):
            row = self.get_data_row(user, request)
            writer.writerow(row)
        return response

    def excel_export(self, request):
        workbook = Workbook()
        worksheet = workbook.active
        response = HttpResponse(
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

        worksheet.append(self.get_headers())
        for user in self.get_queryset(request):
            row = self.get_data_row(user, request)
            worksheet.append(row)

        worksheet.column_dimensions["A"].width = 10
        worksheet.column_dimensions["B"].width = 15
        worksheet.column_dimensions["C"].width = 15
        worksheet.column_dimensions["D"].width = 15
        worksheet.column_dimensions["E"].width = 20
        worksheet.column_dimensions["F"].width = 20
        worksheet.column_dimensions["G"].width = 10

        virtual_excel_file = save_virtual_workbook(workbook)
        response["Content-Disposition"] = (
            f"attachment; filename={self.get_file_name()}.xlsx"
        )
        response["Content-Type"] = "application/octet-stream"
        response.write(virtual_excel_file)
        return response