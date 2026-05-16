"""Category model for Bangazon API"""

from django.db import models


class ProductCategory(models.Model):
    """ProductCategory model for Bangazon API"""

    name = models.CharField(max_length=55)
    description = models.CharField(max_length=255, blank=True, null=True)
    parent_category = models.ForeignKey(
        "self", on_delete=models.CASCADE, null=True, blank=True
    )

    class Meta:
        verbose_name = "productcategory"
        verbose_name_plural = "productcategories"
