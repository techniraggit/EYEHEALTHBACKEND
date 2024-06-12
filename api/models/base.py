from django.db import models
from django.utils import timezone
from uuid import uuid4


class SoftDeleteManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(deleted__isnull=True)


class SoftDeleteMixin(models.Model):
    deleted = models.DateTimeField(null=True, blank=True, default=None)

    def delete(self, using=None, keep_parents=False):
        self.deleted = timezone.now()
        self.save()

    def restore(self):
        self.deleted = None
        self.save()

    def is_deleted(self):
        return self.deleted is not None

    class Meta:
        abstract = True


class BaseModel(models.Model):
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
