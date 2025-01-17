from django.contrib import admin
from ai_doctor.models.models import ChatHistory


# Register your models here.
@admin.register(ChatHistory)
class ChatHistoryAdmin(admin.ModelAdmin):
    list_display = ["id", "user", "query", "response", "created_at"]
    search_fields = ["user", "query"]
    list_filter = ["user"]
    ordering = ["created_at"]
