"""Report View Functions for the Bangazon API"""

from django.shortcuts import render
from bangazonapi.models import Order


def completed_orders_report(request):
    """View function to generate a report of completed orders."""

    # Query the Order model to get all completed orders
    # Currently: Completed orders are defined as those with a non-null payment_type
    # TODO: Update the definition of completed orders when we implement a completed_date field in the Order model
    completed_orders = (
        Order.objects.filter(payment_type__isnull=False)
        .prefetch_related("lineitems__product")
        .select_related("customer__user", "payment_type")
        .all()
    )
    # Note: prefetch_related is used do reverse lookups on the OrderProduct model to get the related Product objects for each line item in the order
    # Note: The select_related method is used to optimize database queries by fetching related objects in a single query, reducing the number of database hits
    # Note: customer__user is used to access the related User model through the Customer model

    # Prepare the context for the template. This allows you to access the completed_orders data in the HTML template
    context = {"completed_orders": completed_orders}

    # Render the 'completed_orders.html' template with the context data
    return render(request, "reports/completed_orders.html", context)
