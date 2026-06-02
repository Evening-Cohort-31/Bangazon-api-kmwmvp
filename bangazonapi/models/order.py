"""Model for Customer Order"""

from datetime import date
from django.db import models
from .customer import Customer
from .payment import Payment


class Order(models.Model):
    customer = models.ForeignKey(
        Customer,
        on_delete=models.DO_NOTHING,
    )
    payment_type = models.ForeignKey(Payment, on_delete=models.DO_NOTHING)
    created_date = models.DateField(default=date.today)

    # add a total property to the model giving the total of the order based on its lineitems
    @property
    def total(self):
        return sum(item.product.price for item in self.lineitems.all()) # type: ignore[attr-defined]
