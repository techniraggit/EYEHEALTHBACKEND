from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from admin_panel.views.base import AdminLoginView
from django.shortcuts import render
from django.core.paginator import Paginator
from store.models.products import Frame


class FramesView(AdminLoginView):
    def get(self, request):
        companies = Frame.objects.all()
        paginator = Paginator(companies, 10)
        page_number = request.GET.get("page")
        paginated_frames = paginator.get_page(page_number)
        context = dict(
            paginated_frames=paginated_frames,
            is_frames=True,
        )
        return render(request, "products/frame_listing.html", context)


class UpdateFramesRecommendation(AdminLoginView):
    def post(self, request):
        frame_id = request.POST.get("id")
        frame_obj = get_object_or_404(Frame, id=frame_id)
        frame_obj.is_recommended = not frame_obj.is_recommended
        frame_obj.save()
        return JsonResponse(
            {"success": True, "is_recommended": frame_obj.is_recommended}
        )
