"""View module for handling requests about customer shopping cart"""

from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework import status, serializers
from bangazonapi.models import Customer, Product, Cart, CartProduct
from .product import LineItemProductSerializer


class CartLineItemSerializer(serializers.ModelSerializer):
    """Nested Serializer for Lineitems (cart items) inside the Cart"""

    product = LineItemProductSerializer()

    class Meta:
        model = CartProduct
        fields = ("product",)


class CartSerializer(serializers.ModelSerializer):
    """JSON serializer for cart"""

    # set many=True because a cart can have many line items
    # set read_only=True since the serializer is only used to display line items in the cart, not create them
    lineitems = CartLineItemSerializer(many=True, read_only=True)
    total = serializers.SerializerMethodField()
    size = serializers.SerializerMethodField()

    def get_size(self, obj):
        return obj.lineitems.count()

    def get_total(self, obj):
        return sum([item.product.price for item in obj.lineitems.all()])

    class Meta:
        model = Cart
        fields = ["id", "customer", "lineitems", "total", "size"]


class CartViewSet(ViewSet):
    """Shopping cart for Bangazon eCommerce"""

    def list(self, request):
        """
        @api {GET} /cart GET line items in cart
        @apiName GetCart
        @apiGroup ShoppingCart

        @apiSuccess (200) {Number} id Cart id
        @apiSuccess (200) {String} customer Customer name
        @apiSuccess (200) {Number} size Number of items in cart
        @apiSuccess (200) {Object[]} lineitems Line items in cart
        @apiSuccess (200) {Number} lineitems.id Line item id
        @apiSuccess (200) {Object} lineitems.product Product in cart
        @apiSuccess (200) {Number} total Total price of items in cart
        @apiSuccessExample {json} Success
            {
                "id": 2,
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
                ],
                "total": 1296.98,
                "size": 1
            }
        """
        current_user = Customer.objects.get(user=request.auth.user)
        user_cart, _ = Cart.objects.get_or_create(customer=current_user)

        serialized_cart = CartSerializer(user_cart, context={"request": request})
        return Response(serialized_cart.data)

    def create(self, request):
        """
        @api {POST} /cart POST new line items to cart
        @apiName AddLineItem
        @apiGroup ShoppingCart

        @apiSuccessExample {json} Success
            HTTP/1.1 201 Created
        @apiParam {Number} product_id Id of product to add
        """
        current_user = Customer.objects.get(user=request.auth.user)

        user_cart, _ = Cart.objects.get_or_create(customer=current_user)

        line_item = CartProduct()
        line_item.product = Product.objects.get(pk=request.data["product_id"])
        line_item.cart = user_cart
        line_item.save()

        serialized_cart = CartLineItemSerializer(
            line_item, context={"request": request}
        )
        return Response(serialized_cart.data, status=status.HTTP_201_CREATED)

    def destroy(self, request, pk=None):
        """
        @api {DELETE} /cart/:id DELETE line item from cart
        @apiName RemoveLineItem
        @apiGroup ShoppingCart

        @apiParam {id} id Product Id to remove from cart
        @apiSuccessExample {json} Success
            HTTP/1.1 204 No Content
        """
        try:
            current_user = Customer.objects.get(user=request.auth.user)
            order_product = CartProduct.objects.get(pk=pk, cart__customer=current_user)
            order_product.delete()

            return Response({}, status=status.HTTP_204_NO_CONTENT)

        except CartProduct.DoesNotExist as ex:
            return Response({"message": ex.args[0]}, status=status.HTTP_404_NOT_FOUND)

        except Exception as ex:
            return Response(
                {"message": ex.args[0]}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=["delete"], url_path="")
    def delete_all(self, request):

        current_user = Customer.objects.get(user=request.auth.user)
        open_order = Cart.objects.get(customer=current_user)
        CartProduct.objects.filter(cart=open_order).delete()

        return Response({}, status=status.HTTP_204_NO_CONTENT)
