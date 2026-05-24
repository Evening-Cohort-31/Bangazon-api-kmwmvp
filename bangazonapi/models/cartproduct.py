"""Model for CartProduct"""

from django.db import models


class CartProduct(models.Model):

    cart = models.ForeignKey(
        "Cart", on_delete=models.DO_NOTHING, related_name="lineitems"
    )

    product = models.ForeignKey(
        "Product", on_delete=models.DO_NOTHING, related_name="+"
    )
