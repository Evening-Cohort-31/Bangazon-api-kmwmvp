"""View module for handling requests about customer profiles"""

from django.http import HttpResponseServerError
from django.contrib.auth.models import User
from rest_framework import serializers, status
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet
from bangazonapi.models import (
    Customer,
    Product,
    OrderProduct,
    Recommendation,
    Favorite,
    Store,
)
from .product import ProductSerializer


class ProfileViewSet(ViewSet):
    """Request handlers for user profile info in the Bangazon Platform"""

    permission_classes = (IsAuthenticatedOrReadOnly,)

    def list(self, request):
        """
        @api {GET} /profile GET user profile info
        @apiName GetProfile
        @apiGroup UserProfile

        @apiHeader {String} Authorization Auth token
        @apiHeaderExample {String} Authorization
            Token 9ba45f09651c5b0c404f37a2d2572c026c146611

        @apiSuccess (200) {Number} id Profile id
        @apiSuccess (200) {Object} user Related user object
        @apiSuccess (200) {String} user.first_name Customer first name
        @apiSuccess (200) {String} user.last_name Customer last name
        @apiSuccess (200) {String} user.email Customer email
        @apiSuccess (200) {String} phone_number Customer phone number
        @apiSuccess (200) {String} address Customer address
        @apiSuccess (200) {Object[]} payment_types Array of user's payment types
        @apiSuccess (200) {Object[]} recommends Array of recommendations made by the user

        @apiSuccessExample {json} Success
            HTTP/1.1 200 OK
            {
                "id": 7,
                "user": {
                    "first_name": "Brenda",
                    "last_name": "Long",
                    "email": "brenda@brendalong.com"
                },
                "phone_number": "555-1212",
                "address": "100 Indefatiguable Way",
                "payment_types": [
                    {
                        "deleted": null,
                        "merchant_name": "Visa",
                        "account_number": "fj0398fjw0g89434",
                        "expiration_date": "2020-03-01",
                        "create_date": "2019-03-11",
                    }
                ],
                "recommends": [
                    {
                        "product": {
                            "id": 32,
                            "name": "DB9"
                        },
                        "customer": {
                            "id": 5,
                            "user": {
                                "first_name": "Joe",
                                "last_name": "Shepherd",
                                "email": "joe@joeshepherd.com"
                            }
                        }
                    }
                ]
            }
        """
        try:
            current_user = Customer.objects.get(user=request.auth.user)
            current_user.recommends = Recommendation.objects.filter(
                recommender=current_user
            )

            serializer = ProfileSerializer(
                current_user, many=False, context={"request": request}
            )

            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as ex:
            return HttpResponseServerError(ex)


class LineItemSerializer(serializers.HyperlinkedModelSerializer):
    """JSON serializer for products in the user's profile recommends section"""

    product = ProductSerializer(many=False)

    class Meta:
        model = OrderProduct
        fields = ("id", "product")


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


class ProfileProductSerializer(serializers.ModelSerializer):
    """JSON serializer for products liked by the user in their profile"""

    class Meta:
        model = Product
        fields = (
            "id",
            "name",
        )


class RecommenderSerializer(serializers.ModelSerializer):
    """JSON serializer for recommendations"""

    customer = CustomerSerializer()
    product = ProfileProductSerializer()

    class Meta:
        model = Recommendation
        fields = (
            "product",
            "customer",
        )


class SellerSerializer(serializers.ModelSerializer):
    """JSON serializer for SELLER (store owner)"""

    first_name = serializers.CharField(source="user.first_name")
    last_name = serializers.CharField(source="user.last_name")

    class Meta:
        model = Customer
        fields = ["first_name", "last_name"]


class StoreSerializer(serializers.ModelSerializer):
    """JSON serializer for store dropping description"""

    seller = SellerSerializer(source="customer", many=False)

    class Meta:
        model = Store
        fields = ["id", "name", "seller"]


class FavoriteStoreSerializer(serializers.ModelSerializer):
    """Serializer for Favorites to only expose id and nested seller info since customer_id is implied by the endpoint"""

    store = StoreSerializer(many=False)

    class Meta:
        model = Favorite
        fields = ("id", "store")


class ProfileSerializer(serializers.ModelSerializer):
    """JSON serializer for customer profile"""

    user = UserSerializer(many=False)
    recommends = RecommenderSerializer(many=True)
    store = StoreSerializer(many=False, read_only=True)
    likes = ProfileProductSerializer(source="liked_products", many=True)
    favorite_stores = FavoriteStoreSerializer(source="favorites", many=True)

    class Meta:
        model = Customer
        fields = (
            "id",
            "user",
            "phone_number",
            "address",
            "payment_types",
            "recommends",
            "store",
            "likes",
            "favorite_stores",
        )

        # use depth=1 to automatically serialize nested payment types since there is no custom serializer for them
        depth = 1
