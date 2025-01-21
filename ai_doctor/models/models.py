from .base import BaseModel, models
from api.models.accounts import UserModel


class ChatHistory(BaseModel):
    user = models.ForeignKey(
        UserModel, on_delete=models.SET_NULL, null=True, related_name="ai_chat_history"
    )
    query = models.TextField()
    response = models.TextField()

    class Meta:
        ordering = ["-created_at"]
        verbose_name_plural = "Chat History"
        verbose_name = "Chat History"

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)

    class Meta:
        verbose_name_plural = "Categories"
        verbose_name = "Category"
        ordering = ["name"]
    
    def __str__(self):
        return f"{self.name}"

class PredefinedPrompts(BaseModel):
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name="prompts")
    prompt = models.TextField()

    class Meta:
        verbose_name_plural = "Predefined Prompts"
        verbose_name = "Predefined Prompt"

    def __str__(self):
        return f"{self.prompt}"

    @classmethod
    def get_random_prompt(cls):
        return cls.objects.order_by("?").first()

    @classmethod
    def get_all_prompts_as_list(cls):
        return list(cls.objects.values_list("prompt", flat=True))
