"""Report View Functions for the Bangazon API"""

from django.shortcuts import render
from bangazonapi.models import Order, Cart, Product, Customer


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

def pending_orders_report(request):
    """View function to generate a report of incomplete orders now called pending orders"""

    # Follows the same pattern as  completed_orders_report only queries the Cart model as reference instead of Orders.
    pending_orders = (
        Cart.objects.filter()
        .prefetch_related("lineitems__product")
        .select_related("customer")
        .all()
    )


    context = {"pending_orders": pending_orders}

    # Renders as 'pending_orders.html' template using the context data
    return render(request, "reports/pending_orders.html", context)

def inexpensive_products_report(request):
    """View function to generate a report of products priced at $999 or less"""

    inexpensive_products = (
        Product.objects.filter(price__lte=999)
        .order_by("price")
    )

    context = {"inexpensive_products": inexpensive_products}

    return render(request, "reports/inexpensive_products.html", context)

def expensive_products_report(request):
    """View function to generate a report of products priced at $1000 or more"""

    expensive_products = (
        Product.objects.filter(price__gte=1000)
        .order_by("price")
    )

    context = {"expensive_products": expensive_products}

    return render(request, "reports/expensive_products.html", context)

def favorite_sellers_report(request):
    """View function to generate a report of sellers that have been favorites by customers"""

    favorite_sellers = (
        Customer.objects.prefetch_related("favorites__store__customer__user")
        .filter(favorites__isnull=False)
        .distinct()
    )

    context = {"favorite_sellers": favorite_sellers}

    return render(request, "reports/favorite_sellers.html")



# End-of-File (EOF)
