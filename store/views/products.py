from store.views.base import UserMixin
from store.models.products import Frame
from store.serializers import FrameSerializer
from core.utils import api_response


class FramesView(UserMixin):
    def get(self, request):
        qs = Frame.objects.all()
        data = FrameSerializer(qs, many=True).data
        return api_response(True, 200, data=data)
