"""View Module for Handling Requests about Customer Favorites"""

import datetime
from PIL.Image import item
from django.http import HttpResponseServerError
from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework import serializers, status
from bangazonapi.models import Order, Payment, Customer, OrderProduct, Cart, CartProduct
from .product import LineItemProductSerializer
from .paymenttype import PaymentSerializer


class StoreSerializer(serializers.ModelSerializer):
    """JSON serializer for STORE SERIALIZER summary"""

    class Meta:
        model = Store
        fields = ["id", "name", "description"]


class UserSerializer(serializers.ModelSerializer):
    """JSON serializer for customer profile"""

    class Meta:
        model = User
        fields = ("first_name", "last_name", "email")


class CustomerSerializer(serializers.ModelSerializer):
    """JSON serializer for recommendation customers"""

    user = UserSerializer()

    class Meta:
        model = Customer
        fields = (
            "id",
            "user",
        )


class FavoriteSerializer(serializers.ModelSerializer):
    """JSON serializer for customer favorites"""

    store = StoreSerializer()
    customer = CustomerSerializer()

    class Meta:
        model = Order
        fields = (
            "id",
            "customer",
            "store",
        )


class FavoriteViewSet(ViewSet):
    """View for interacting with customer favorites"""

    def retrieve(self, request, pk=None):
        """
        @api {GET} /favorites/:id GET single favorite
        @apiName GetFavorite
        @apiGroup Favorites

        @apiHeader {String} Authorization Auth token
        @apiHeaderExample {String} Authorization
            Token 9ba45f09651c5b0c404f37a2d2572c026c146611

        @apiSuccess (200) {id} id Favorite id
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
            customer_cart = Cart.objects.get(customer=customer)
            payment = Payment.objects.get(pk=request.data["payment_type"])
            created_date = datetime.datetime.now()

            customer_order = Order.objects.create(
                customer=customer, payment_type=payment, created_date=created_date
            )

            for item in CartProduct.objects.filter(cart=customer_cart):
                OrderProduct.objects.create(order=customer_order, product=item.product)

            CartProduct.objects.filter(cart=customer_cart).delete()

            customer_cart.delete()

            return Response({}, status=status.HTTP_204_NO_CONTENT)
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
