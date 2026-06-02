"""View module for handling requests about customer orders"""

import datetime
from PIL.Image import item
from django.http import HttpResponseServerError
from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework import serializers, status
from bangazonapi.models import Order, Payment, Customer, OrderProduct, Cart, CartProduct
from .product import LineItemProductSerializer
from .paymenttype import PaymentSerializer


class OrderLineItemSerializer(serializers.ModelSerializer):
    """JSON serializer for lineitems on an order"""

    product = LineItemProductSerializer()

    class Meta:
        model = OrderProduct
        fields = ("id", "product")


class OrderSerializer(serializers.ModelSerializer):
    """JSON serializer for customer orders"""

    lineitems = OrderLineItemSerializer(many=True, read_only=True)
    payment_type = PaymentSerializer(many=False)
    size = serializers.SerializerMethodField()

    def get_size(self, obj):
        return obj.lineitems.count()

    class Meta:
        model = Order
        fields = (
            "id",
            "created_date",
            "payment_type",
            "customer",
            "lineitems",
            "total",
            "size",
        )


class OrderViewSet(ViewSet):
    """View for interacting with customer orders"""

    def retrieve(self, request, pk=None):
        """
        @api {GET} /orders/:id GET single order
        @apiName GetOrder
        @apiGroup Orders

        @apiHeader {String} Authorization Auth token
        @apiHeaderExample {String} Authorization
            Token 9ba45f09651c5b0c404f37a2d2572c026c146611

        @apiSuccess (200) {id} id Order id
        @apiSuccess (200) {String} created_date Date order was created
        @apiSuccess (200) {String} payment_type Payment URI
        @apiSuccess (200) {String} customer Customer URI

        @apiSuccessExample {json} Success
            {
                "id": 1,
                "created_date": "2019-08-16",
                "payment_type": 1,
                "customer": "Steve Rogers",
                "lineitems": [
                    {
                        "id": 1,
                        "product": {
                            "name": "900",
                            "price": 1296.98,
                            "number_sold": 0,
                            "description": "1987 Saab",
                            "quantity": 2,
                            "created_date": "2019-03-19",
                            "location": "Vratsa",
                            "image_path": null,
                            "average_rating": 0,
                            "category": {
                                    "name": "Auto"
                                },
                            }
                        ],
                "total": 1296.98,
                "size": 1
                    }
        """
        try:
            customer = Customer.objects.get(user=request.auth.user)
            order = Order.objects.get(pk=pk, customer=customer)
            serializer = OrderSerializer(order, context={"request": request})
            return Response(serializer.data)

        except Order.DoesNotExist as ex:
            return Response(
                {
                    "message": "The requested order does not exist, or you do not have permission to access it."
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        except Exception as ex:
            return HttpResponseServerError(ex)

    def create(self, request, pk=None):
        """
        @api {PUT} /orders/:id PUT new payment for order
        @apiName AddPayment
        @apiGroup Orders

        @apiHeader {String} Authorization Auth token
        @apiHeaderExample {String} Authorization
            Token 9ba45f09651c5b0c404f37a2d2572c026c146611

        @apiParam {id} id Order Id route parameter
        @apiParam {id} payment_type Payment Id to pay for the order
        @apiParamExample {json} Input
            {
                "payment_type": 6
            }

        @apiSuccessExample {json} Success
            HTTP/1.1 204 No Content
        """
        customer = Customer.objects.get(user=request.auth.user)
        # Handle case where cart is empty and order is created without line items
        try:
            # Get the customer's cart, payment type, and current date to create the order
            customer_cart = Cart.objects.get(customer=customer)
            payment = Payment.objects.get(pk=request.data["payment_type"])

            # Create the and instance of the order
            customer_order = Order.objects.create(
                customer=customer, payment_type=payment
            )

            # TODO: Handle quantity changes and product availability checks here before creating order products
            # For each item in the cart, create an order product for the line item
            for item in CartProduct.objects.filter(cart=customer_cart):
                OrderProduct.objects.create(order=customer_order, product=item.product)

            # Lasly, clear the cart of all items
            CartProduct.objects.filter(cart=customer_cart).delete()
            customer_cart.delete()

            # Now return the order that was just created with all line items and payment details
            return Response(
                OrderSerializer(customer_order, context={"request": request}).data,
                status=status.HTTP_201_CREATED,
            )
        except Cart.DoesNotExist:
            return Response(
                {"message": "The cart is empty."},
                status=status.HTTP_400_BAD_REQUEST,
            )

    def list(self, request):
        """
        @api {GET} /orders GET customer orders
        @apiName GetOrders
        @apiGroup Orders

        @apiHeader {String} Authorization Auth token
        @apiHeaderExample {String} Authorization
            Token 9ba45f09651c5b0c404f37a2d2572c026c146611

        @apiParam {id} payment_id Query param to filter by payment used

        @apiSuccess (200) {Object[]} orders Array of order objects
        @apiSuccess (200) {id} orders.id Order id
        @apiSuccess (200) {String} orders.created_date Date order was created
        @apiSuccess (200) {String} orders.payment_type Payment URI
        @apiSuccess (200) {String} orders.customer Customer URI

        @apiSuccessExample {json} Success
            [
                {
                    "id": 1,
                    "created_date": "2019-08-16",
                    "payment_type": 1,
                    "customer": "Steve Rogers",
                    "lineitems": [
                        {
                            "id": 52,
                            "product": {
                                "name": "900",
                                "price": 1296.98,
                                "number_sold": 0,
                                "description": "1987 Saab",
                                "quantity": 2,
                                "created_date": "2019-03-19",
                                "location": "Vratsa",
                                "image_path": null,
                                "average_rating": 0,
                                "category": {
                                    "url": "http://localhost:8000/productcategories/2",
                                    "name": "Auto"
                                }
                            }
                        }
                    ]
                }
            ]
        """
        customer = Customer.objects.get(user=request.auth.user)
        orders = Order.objects.filter(customer=customer, payment_type__isnull=False)

        payment = request.query_params.get("payment_id", None)
        if payment is not None:
            orders = orders.filter(payment_type__id=payment)

        json_orders = OrderSerializer(orders, many=True, context={"request": request})

        return Response(json_orders.data)
