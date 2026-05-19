from django.db import models
from .customer import Customer

class Store(models.Model):
    name = models.CharField(max_length=200)
    description = models.CharField(max_length=1000)
    customer = models.ForeignKey(
         Customer, on_delete=models.CASCADE, related_name="stores"
    )
