"""Model for Favorites in Bangazon API"""

from django.db import models
from .customer import Customer


class Favorite(models.Model):

    customer = models.ForeignKey(
        Customer,
        on_delete=models.DO_NOTHING,
    )
    seller = models.ForeignKey(
        Customer, on_delete=models.DO_NOTHING, related_name="favorited_seller"
    )
