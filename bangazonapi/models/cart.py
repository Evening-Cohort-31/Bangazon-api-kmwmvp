"""Customer Cart Model"""

from django.db import models
from .customer import Customer


class Cart(models.Model):
    customer = models.ForeignKey(
        Customer,
        on_delete=models.DO_NOTHING,
    )
