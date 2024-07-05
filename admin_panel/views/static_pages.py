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

class StaticPageDetailedView(AdminLoginView):
    def get(self, request, id):
        try:
            static_page_obj = StaticPages.objects.get(pk=id)
        except StaticPages.DoesNotExist:
            messages.error(request, "Static Page does not exist")
            return redirect("static_pages_view")

        CONTEXT["static_page_obj"] = static_page_obj
        return render(request, "static_pages/view.html", CONTEXT)


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
                {"status": False, "message": f"'{str(title).title()}' page already exists. You can edit this page manually."}
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

        CONTEXT["static_page_obj"] = static_page_obj
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
from weasyprint import HTML, CSS
from django.http import HttpResponse

def generate_legal_pdf(p):
    # Step 1: Render the document without page numbers to get the total page count
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            @page {{
                size: 9.5in 11.6in;
                margin: 1in; /* Adjust the margin as needed */
            }}
        </style>
    </head>
    <body>
        {p.content}
    </body>
    </html>
    """

    html = HTML(string=html_content)
    rendered_html = html.render()
    total_pages = len(rendered_html.pages)

    # Step 2: Render the document again with page numbers and header
    html_content_with_numbers = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            @page {{
                size: 9.5in 11.6in;
                margin: 1in; /* Adjust the margin as needed */
                @top-center {{
                    content: "Created On: {p.created_on.strftime("%Y-%m-%d")} by {p.created_by.get_full_name()}";
                    font-size: 12px;
                    color: gray;
                }}
                @bottom-right {{
                    content: "Page " counter(page) " of {total_pages}";
                    font-size: 12px;
                    font-weight: bold;
                }}
            }}
        </style>
    </head>
    <body style="font-family: sans-serif, ubuntu;">
        {p.content}
    </body>
    </html>
    """

    html_with_numbers = HTML(string=html_content_with_numbers)
    pdf_file = html_with_numbers.write_pdf()
    return pdf_file

import time
class DownloadContentPage(AdminLoginView):
    def get(self, request, id):
        try:
            static_page_obj = StaticPages.objects.get(pk=id)
        except StaticPages.DoesNotExist:
            messages.error(request, "Static Page does not exist")
            return redirect("static_pages_view")
        
        pdf_file = generate_legal_pdf(static_page_obj)

        response = HttpResponse(pdf_file, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{static_page_obj.slug}.pdf"'
        time.sleep(4)
        return response