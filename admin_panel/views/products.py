from utilities.utils import get_form_error_msg
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from admin_panel.views.base import AdminLoginView
from django.shortcuts import render
from django.core.paginator import Paginator
from store.models.products import Frame
from admin_panel.forms.products import FrameForm


class FramesView(AdminLoginView):
    def get(self, request):
        frames = Frame.objects.all().order_by("-created_on")
        paginator = Paginator(frames, 10)
        page_number = request.GET.get("page")
        paginated_frames = paginator.get_page(page_number)
        context = dict(
            paginated_frames=paginated_frames,
            is_frames=True,
        )
        return render(request, "products/frame_listing.html", context)


class FrameDetailView(AdminLoginView):
    def get(self, request, id):
        try:
            frame_obj = Frame.objects.get(id=id)
        except:
            return JsonResponse(
                {
                    "status": False,
                    "message": "Frame does not exist",
                }
            )
        return JsonResponse(
            {
                "status": True,
                "data": frame_obj.to_json(request),
            }
        )


class AddFrameView(AdminLoginView):
    def get(self, request):
        form = FrameForm()
        context = dict(
            form=form,
        )
        return render(request, "products/add_frame.html", context=context)

    def post(self, request):
        form = FrameForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return JsonResponse({"status": True, "message": "Frame added successfully"})
        errors = form.errors.as_json()
        message = get_form_error_msg(errors)
        return JsonResponse({"status": False, "message": message})


class EditFrameView(AdminLoginView):
    def get(self, request, id):
        host_url = f"{request.scheme}://{request.get_host()}"
        print("full_url: ", host_url)

        try:
            frame_obj = Frame.objects.get(id=id)
        except:
            return JsonResponse({"status": False, "message": "Frame not found"})
        form = FrameForm(instance=frame_obj)
        context = dict(
            form=form,
            frame_id=id,
            frame=frame_obj,
            host_url=host_url,
        )
        return render(request, "products/edit_frame.html", context=context)

    def post(self, request, id):
        frame_obj = get_object_or_404(Frame, id=id)
        form = FrameForm(request.POST, request.FILES, instance=frame_obj)
        if form.is_valid():
            form.save()
            return JsonResponse(
                {"status": True, "message": "Frame updated successfully"}
            )
        errors = form.errors.as_json()
        message = get_form_error_msg(errors)
        return JsonResponse({"status": False, "message": message})


class UpdateFramesRecommendation(AdminLoginView):
    def post(self, request):
        frame_id = request.POST.get("id")
        frame_obj = get_object_or_404(Frame, id=frame_id)
        frame_obj.is_recommended = not frame_obj.is_recommended
        frame_obj.save()
        return JsonResponse(
            {"success": True, "is_recommended": frame_obj.is_recommended}
        )
