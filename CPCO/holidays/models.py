from django.db import models

# Create your models here.
class Holiday(models.Model):
    holidays = models.DateField()

    def __str__(self):
        return str(self.holidays)