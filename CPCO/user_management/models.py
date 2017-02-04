from django.db import models
from django.conf import settings


# Create your models here.
class User_info(models.Model):
    user_id = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=None,
    )
    section = models.CharField(max_length = 20)
    name = models.CharField(max_length = 10)
    identity = models.CharField(max_length = 10)

    def __str__(self):
        return str(self.user_id) + "_" + str(self.name)