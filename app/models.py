from django.db import models
from django.contrib.auth.models import User
# Create your models here.

class Company(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, default=None)
    company_name = models.CharField(max_length=50,blank=True)
    company_intial = models.CharField(max_lenght=10,blank=True)

    def __str__(self):
        return self.company_name
