from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from .base import AdminLoginView
from api.models.static_pages import StaticPages


CONTEXT = dict(
    is_static_page=True,
)


class StaticPageView(AdminLoginView):
    def get(self, request):
        search = request.GET.get("search", "").strip()
        static_pages_qs = StaticPages.objects.all().order_by("-created_on")

        if search:
            static_pages_qs = static_pages_qs.filter(
                Q(title__icontains=search)
            )

        paginator = Paginator(static_pages_qs, 10)
        page_number = request.GET.get("page")
        paginated_static_pages_data = paginator.get_page(page_number)

        CONTEXT["static_pages"] = paginated_static_pages_data
        return render(request, "static_pages/listing.html", CONTEXT)


class AddStaticPageView(AdminLoginView):
    def get(self, request):
        return render(request, "static_pages/add.html", context=CONTEXT)

    def post(self, request):
        title = request.POST.get("title")
        content = request.POST.get("content")

        if not title or not content:
            return JsonResponse(
                {"status": False, "message": "Required fields are missing"}
            )

        if StaticPages.objects.filter(title=title).exists():
            return JsonResponse(
                {"status": False, "message": "Page with the same title already exists. You can edit this page manually."}
            )

        try:
            StaticPages.objects.create(
                title=title, content=content, created_by=request.user
            )
            return JsonResponse({"status": True, "message":f"{str(title).title()} Created Successfully"})
        except Exception as e:
            print(e)
            return JsonResponse(
                {
                    "status": False,
                    "message": f"Failed to create {str(title).title()} Page",
                }
            )

class EditStaticPageView(AdminLoginView):
    def get(self, request, id):
        try:
            static_page_obj = StaticPages.objects.get(pk=id)
        except StaticPages.DoesNotExist:
            messages.error(request, "Static Page does not exist")
            return redirect("static_pages_view")

        CONTEXT["static_page"] = static_page_obj
        return render(request, "static_pages/edit.html", context=CONTEXT)

    def post(self, request, id):
        try:
            static_page_obj = StaticPages.objects.get(pk=id)
            title = request.POST.get("title")
            content = request.POST.get("content")

            if not content:
                return JsonResponse(
                    {"status": False, "message": "Required fields are missing"}
                )

            static_page_obj.title = title
            static_page_obj.content = content
            static_page_obj.save()
            return JsonResponse({"status": True, "message": f"{str(title).title()} Updated Successfully"})
        except Exception as e:
            print(e)
            return JsonResponse(
                {
                    "status": False,
                    "message": f"Failed to update {str(static_page_obj.title).title()} Page",
                }
            )