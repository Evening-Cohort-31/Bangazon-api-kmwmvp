"""Model for Payment Types"""

from datetime import date
from safedelete.models import SafeDeleteModel
from safedelete.config import SOFT_DELETE
from django.db import models
from .customer import Customer


class Payment(SafeDeleteModel):
    """Model for Payment Types"""

    _safedelete_policy = SOFT_DELETE
    merchant_name = models.CharField(
        max_length=25,
    )
    account_number = models.CharField(max_length=25)
    customer = models.ForeignKey(
        Customer, on_delete=models.DO_NOTHING, related_name="payment_types"
    )
    expiration_date = models.DateField(default=date.today)
    create_date = models.DateField(default=date.today)
