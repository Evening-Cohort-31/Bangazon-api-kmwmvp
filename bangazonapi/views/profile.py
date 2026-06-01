"""View module for handling requests about customer profiles"""

from django.http import HttpResponseServerError
from django.contrib.auth.models import User
from rest_framework import serializers, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet
from bangazonapi.models import (
    Customer,
    Product,
    OrderProduct,
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
            serializer = ProfileSerializer(
                current_user, many=False, context={"request": request}
            )

            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as ex:
            return HttpResponseServerError(ex)

    # TODO: Refactor this endpoint into its own viewset since it is a different resource than the rest of the profile info and has multiple methods for different HTTP verbs
    @action(
        methods=["get", "post", "delete"],
        detail=False,
        url_path="favoritestores",
        permission_classes=[IsAuthenticated],
    )
    def favoritestores(self, request):
        """Favorite stores endpoint for user profile to view and add favorite stores"""

        # Get current user profile
        customer = Customer.objects.get(user=request.auth.user)

        if request.method == "GET":
            """
            @api {GET} /profile/favoritestores GET favorite stores
            @apiName GetFavoriteStores
            @apiGroup UserProfile

            @apiHeader {String} Authorization Auth token
            @apiHeaderExample {String} Authorization
                Token 9ba45f09651c5b0c404f37a2d2572c026c146611

            @apiSuccess (200) {id} id Favorite id
            @apiSuccess (200) {Object} store Favorited store
            @apiSuccess (200) {String} store.name Store name
            @apiSuccess (200) {String} seller.first_name Store owner's first name
            @apiSuccess (200) {String} seller.last_name Store owner's last name
            @apiSuccessExample {json} Success
                [
                    {
                        "id": 1,
                        "store": {
                            "name": "Steve's Store",
                            "seller": {
                                "first_name": "Steve",
                                "last_name": "Smith"
                            },
                        }
                    },
                    {
                        "id": 2,
                        "store": {
                            "name": "Brenda's Store",
                            "seller": {
                                "first_name": "Brenda",
                                "last_name": "Johnson"
                            },
                        }
                    },
                    {
                        "id": 3,
                        "store": {
                            "name": "Charlie's Store",
                            "seller": {
                                "first_name": "Charlie",
                                "last_name": "Brown"
                            }
                        }
                    }
                ]
            """
            favorites = Favorite.objects.filter(customer=customer)

            serializer = FavoriteStoreSerializer(
                favorites, many=True, context={"request": request}
            )
            return Response(serializer.data)

        if request.method == "POST":
            """
            @api {POST} /profile/favoritestores POST new favorite store
            @apiName AddFavoriteStore
            @apiGroup UserProfile

            @apiHeader {String} Authorization Auth token
            @apiHeaderExample {String} Authorization
                Token 9ba45f09651c5b0c404f37a2d2572c026c146611

            @apiParam {Number} store_id Id of store to favorite

            @apiSuccess (200) {id} id Favorite id
            @apiSuccess (200) {Object} store Favorited store
            @apiSuccess (200) {String} store.name Store name
            @apiSuccess (200) {String} seller.first_name Store owner's first name
            @apiSuccess (200) {String} seller.last_name Store owner's last name
            @apiSuccessExample {json} Success
                {
                    "id": 4,
                    "store": {
                        "name": "Steve's Store",
                        "seller": {
                            "first_name": "Steve",
                            "last_name": "Smith"
                        }
                    }
                }
            """
            try:
                new_favorite = Favorite()
                new_favorite.customer = customer
                new_favorite.store = Store.objects.get(pk=request.data["store_id"])

                if Favorite.objects.filter(
                    customer=customer, store=new_favorite.store
                ).exists():
                    return Response(
                        {"message": "This store is already in your favorites list."},
                        status=status.HTTP_409_CONFLICT,
                    )

                new_favorite.save()

                serializer = FavoriteStoreSerializer(
                    new_favorite, many=False, context={"request": request}
                )
                return Response(serializer.data, status=status.HTTP_201_CREATED)

            except Store.DoesNotExist as ex:
                return Response(
                    {"message": ex.args[0]}, status=status.HTTP_404_NOT_FOUND
                )

        if request.method == "DELETE":
            """
            @api {DELETE} /profile/favoritestores DELETE a favorite store
            @apiName DeleteFavoriteStore
            @apiGroup UserProfile

            @apiHeader {String} Authorization Auth token
            @apiHeaderExample {String} Authorization
                Token 9ba45f09651c5b0c404f37a2d2572c026c146611

            @apiParam {Number} store_id Id of store to remove from favorites

            @apiSuccess (204) NoContent Successfully removed favorite store
            @apiError (404) NotFound The specified store was not found in the user's favorites list
            """
            try:
                favorite_to_delete = Favorite.objects.get(
                    customer=customer, store__id=request.data["store_id"]
                )
                favorite_to_delete.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            except Favorite.DoesNotExist:
                return Response(
                    {"message": "This store is not in your favorites list."},
                    status=status.HTTP_404_NOT_FOUND,
                )


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
            # "recommends",
            "store",
            "likes",
            "favorite_stores",
        )

        # use depth=1 to automatically serialize nested payment types since there is no custom serializer for them
        depth = 1
