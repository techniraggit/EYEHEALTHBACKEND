from django.db import models

# Create your models here.
class Credentials(models.Model):
    name = models.CharField(max_length=255,unique=True)
    data = models.JSONField()
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
    
    def to_json(self):
        return dict(
            name=self.name,
            data=self.data,
            created_on=self.created_on,
            updated_on=self.updated_on,
        )
