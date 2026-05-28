"""View Module for Handling Requests about Customer Favorites"""

from django.contrib.auth.models import User
from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework import serializers, status
from bangazonapi.models import Customer, Favorite, Store


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


class SellerSerializer(serializers.ModelSerializer):
    """JSON serializer for SELLER (store owner)"""

    first_name = serializers.CharField(source="user.first_name")
    last_name = serializers.CharField(source="user.last_name")

    class Meta:
        model = Customer
        fields = ["first_name", "last_name"]


class FavoritesStoreSerializer(serializers.ModelSerializer):
    """JSON serializer for STORE SERIALIZER summary"""

    seller = SellerSerializer(source="customer", read_only=True)

    class Meta:
        model = Store
        fields = ["id", "name", "description", "seller"]


class FavoriteSerializer(serializers.ModelSerializer):
    """JSON serializer for customer favorites"""

    store = FavoritesStoreSerializer()
    customer = CustomerSerializer()

    class Meta:
        model = Favorite
        fields = (
            "id",
            "customer",
            "store",
        )


class ListFavoriteSerializer(serializers.ModelSerializer):
    """JSON serializer for listing customer favorites"""

    store = FavoritesStoreSerializer()
    # omits customer details for list view since it's the same for all favorites in the list

    class Meta:
        model = Favorite
        fields = (
            "id",
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
        @apiSuccess (200) {Object} customer Customer object
        @apiSuccess (200) {Object} store Store object

        @apiSuccessExample {json} Success
            {
                "id": 1,
                "customer": {
                    "id": 1,
                    "user": {
                        "first_name": "Steve",
                        "last_name": "Rogers",
                        "email": "steve.rogers@example.com"
                            }
                        },
                "store": {
                    "id": 1,
                    "name": "Rogers' Used Cars",
                    "description": "A variety of used cars for sale",
                    "seller": {
                        "first_name": "Steve",
                        "last_name": "Rogers"
                                }
                        }
            }
        """
        try:
            customer = Customer.objects.get(user=request.auth.user)
            favorite = Favorite.objects.get(pk=pk, customer=customer)
            serializer = FavoriteSerializer(favorite, context={"request": request})
            return Response(serializer.data)

        except (Favorite.DoesNotExist, Customer.DoesNotExist):
            return Response(
                {
                    "message": "The requested favorite does not exist, or you do not have permission to access it."
                },
                status=status.HTTP_404_NOT_FOUND,
            )

    def create(self, request, pk=None):
        """
        @api {PUT} /favorites/:id PUT new favorite for customer
        @apiName AddFavorite
        @apiGroup Favorites

        @apiHeader {String} Authorization Auth token
        @apiHeaderExample {String} Authorization
            Token 9ba45f09651c5b0c404f37a2d2572c026c146611

        @apiParam {id} id Favorite Id route parameter
        @apiParam {id} store_id Store Id to add to favorites
        @apiParamExample {json} Input
            {
                "store_id": 6
            }

        @apiSuccessExample {json} Success
            HTTP/1.1 204 No Content
        """

        try:
            customer = Customer.objects.get(user=request.auth.user)
            store = Store.objects.get(pk=request.data["store_id"])
            if Favorite.objects.filter(customer=customer, store=store).exists():
                return Response(
                    {"message": "This store is already in your favorites."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            favorite = Favorite()
            favorite.customer = customer
            favorite.store = store
            favorite.save()
            return Response(None, status=status.HTTP_204_NO_CONTENT)

        except Customer.DoesNotExist:
            return Response(
                {"message": "You do not have permission to add favorites."},
                status=status.HTTP_404_NOT_FOUND,
            )

        except Store.DoesNotExist:
            return Response(
                {"message": "The requested store does not exist."},
                status=status.HTTP_404_NOT_FOUND,
            )

        except KeyError:
            return Response(
                {"message": "a store_id is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

    def list(self, request):
        """
        @api {GET} /favorites GET customer favorites
        @apiName GetFavorites
        @apiGroup Favorites

        @apiHeader {String} Authorization Auth token
        @apiHeaderExample {String} Authorization
            Token 9ba45f09651c5b0c404f37a2d2572c026c146611

        @apiParam {id} store_id Query param to filter by store id

        @apiSuccess (200) {Object[]} favorites Array of favorite objects
        @apiSuccess (200) {id} favorites.id Favorite id
        @apiSuccess (200) {Object} favorites.created_date Date favorite was created
        @apiSuccess (200) {Object} favorites.store Store URI
        @apiSuccess (200) {Object} favorites.customer Customer URI

        @apiSuccessExample {json} Success
            [
                {
                    "id": 1,
                    "store": {
                        "id": 1,
                        "name": "Rogers' Used Cars",
                        "description": "A variety of used cars for sale",
                        "seller": {
                            "first_name": "Steve",
                            "last_name": "Rogers"
                        }
                    },
                    "customer": {
                        "id": 1,
                        "user": {
                            "first_name": "Steve",
                            "last_name": "Rogers",
                            "email": "steve.rogers@example.com"
                        }
                    }
                }
            ]
        """
        try:
            customer = Customer.objects.get(user=request.auth.user)
            favorites = Favorite.objects.filter(customer=customer)

            store = request.query_params.get("store_id", None)
            if store is not None:
                favorites = favorites.filter(store__id=store)

            json_favorites = ListFavoriteSerializer(
                favorites, many=True, context={"request": request}
            )

            return Response(json_favorites.data)

        except Customer.DoesNotExist:
            return Response(
                {"message": "You do not have permission to access these favorites."},
                status=status.HTTP_404_NOT_FOUND,
            )

    def destroy(self, request, pk=None):
        """
        @api {DELETE} /favorites/:id DELETE favorite
        @apiName DeleteFavorite
        @apiGroup Favorites

        @apiHeader {String} Authorization Auth token
        @apiHeaderExample {String} Authorization
            Token 9ba45f09651c5b0c404f37a2d2572c026c146611

        @apiParam {id} id Favorite Id route parameter

        @apiSuccessExample {json} Success
            HTTP/1.1 204 No Content
        """
        try:
            customer = Customer.objects.get(user=request.auth.user)
            favorite = Favorite.objects.get(pk=pk, customer=customer)
            favorite.delete()
            return Response(None, status=status.HTTP_204_NO_CONTENT)

        except (Favorite.DoesNotExist, Customer.DoesNotExist):
            return Response(
                {
                    "message": "The requested favorite does not exist, or you do not have permission to delete it."
                },
                status=status.HTTP_404_NOT_FOUND,
            )
