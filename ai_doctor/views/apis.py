from ai_doctor.views.base import UserMixin
from core.utils import api_response
from ai_doctor.gemini import make_request
from django_q.tasks import async_task
from ai_doctor.models.models import ChatHistory, PredefinedPrompts


def save_chat_history(user, query, response):
    try:
        ChatHistory.objects.create(user=user, query=query, response=response)
    except Exception as e:
        print(f"Error storing chat history: {e}")


class AskDoctorView(UserMixin):
    def post(self, request):
        query = request.data.get("query")
        if not query:
            return api_response(False, 400, "Query required")

        try:
            ai_doctor_response = make_request(query)
            async_task(save_chat_history, request.user, query, ai_doctor_response)
            return api_response(True, 200, query=query, response=ai_doctor_response)
        except Exception as e:
            return api_response(
                False, 500, message=f"Error processing AI Doctor request: {e}"
            )


class PredefinedPromptsView(UserMixin):
    def get(self, request):
        try:
            prompts = PredefinedPrompts.get_all_prompts_as_list()
            return api_response(True, 200, prompts=prompts)
        except Exception as e:
            return api_response(False, 500, message=str(e))
