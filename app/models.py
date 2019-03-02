from django.db import models
from django.contrib.auth.models import User


class Company(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, default=None)
    company_name = models.CharField(max_length=50, blank=True)
    company_intial = models.CharField(max_length=10, blank=True)
    amount_of_stock = models.IntegerField()
    purchase_price = models.FloatField()
    stoploss = models.FloatField()
    to_sell = models.CharField(max_length=3, default="No")

    def __str__(self):
        return self.company_name
