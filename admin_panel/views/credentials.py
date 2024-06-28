from .base import AdminLoginView
from django.shortcuts import render
from django.http import JsonResponse
from admin_panel.models import Credentials


class CredentialsView(AdminLoginView):
    def get(self, request):
        credentials_qs = Credentials.objects.all().order_by("-created_on")

        context = dict(
            is_credentials=True,
            credentials_qs=credentials_qs,
        )
        return render(request, "credentials/credentials.html", context)


class AddCredentialsView(AdminLoginView):
    def post(self, request):
        query_dict = request.POST
        raw_qd = query_dict.copy()
        raw_qd = dict(raw_qd)
        raw_qd.pop("csrfmiddlewaretoken", None)
        raw_qd.pop("name", None)
        length = int(len(raw_qd.keys())/2) + 1

        name = query_dict.get("name")
        keys = [query_dict.get(f'key{i}') for i in range(1, length)]
        values = [query_dict.get(f'value{i}') for i in range(1, length)]

        key_value_pairs = dict(zip(keys, values))

        if Credentials.objects.filter(name=name).exists():
            return JsonResponse(dict(
                status=False,
                message="Credentials with this name already exists",
            ))

        try:
            Credentials.objects.create(
                name=name,
                data=key_value_pairs,
            )
            return JsonResponse(
                dict(
                    status=True,
                    message="Credentials added successfully",
                )
            )
        except Exception as e:
            return JsonResponse(
                dict(status=False, message="Credentials not added", error=str(e))
            )


class UpdateCredentialsView(AdminLoginView):
    def post(self, request, id):
        request_data = dict(request.POST)
        request_data.pop("csrfmiddlewaretoken", None)
        for key, value in request_data.items():
            request_data[key] = value[0]

        try:
            credentials_obj = Credentials.objects.get(pk=id)
        except:
            return JsonResponse(
                dict(
                    status=False,
                    message="Credentials does not exist",
                )
            )

        try:
            credentials_obj.data = request_data
            credentials_obj.save()
            return JsonResponse(
                dict(
                    status=True,
                    message="Credentials updated successfully",
                )
            )
        except Exception as e:
            return JsonResponse(
                dict(status=False, message="Credentials not updated", error=str(e))
            )

class DeleteCredentialsView(AdminLoginView):
    def get(self, request, id):
        try:
            credentials_obj = Credentials.objects.get(pk=id)
            credentials_obj.delete()
            return JsonResponse(
                dict(
                    status=True,
                    message="Credentials deleted successfully",
                )
            )
        except:
            return JsonResponse(
                dict(
                    status=False,
                    message="Credentials does not exist",
                )
            )