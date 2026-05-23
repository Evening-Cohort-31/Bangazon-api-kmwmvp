"""Model for Customer Cart"""

from django.db import models
from .customer import Customer


class Cart(models.Model):
    customer = models.ForeignKey(
        Customer,
        on_delete=models.DO_NOTHING,
    )

    # add a total property to the model giving the total of the order based on its lineitems
    @property
    def total(self):
        return sum(item.product.price for item in self.lineitems.all()) # type: ignore[attr-defined]