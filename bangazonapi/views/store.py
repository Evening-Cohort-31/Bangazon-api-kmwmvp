from rest_framework import (
    serializers,
    status,
    permissions,
    viewsets,
    response,
)

from bangazonapi.models import Customer, Store, Favorite, customer, customer


class SellerSerializer(serializers.ModelSerializer):
    """JSON serializer for SELLER (store owner)"""

    first_name = serializers.CharField(source="user.first_name")
    last_name = serializers.CharField(source="user.last_name")

    class Meta:
        model = Customer
        fields = ["first_name", "last_name"]


class StoreSerializer(serializers.ModelSerializer):
    """JSON serializer for STORE SERIALIZER summary"""

    seller = SellerSerializer(source="customer", read_only=True)

    is_favorite = serializers.SerializerMethodField()

    def get_is_favorite(self, obj):
        """Method to determine if the store is a favorite of the current user"""

        user = self.context["request"].user
        if not user.is_authenticated:
            return False

        customer_owning_store = obj.customer
        user_customer_profile = Customer.objects.get(user=user)

        return Favorite.objects.filter(
            customer=user_customer_profile, seller=customer_owning_store
        ).exists()

    class Meta:
        model = Store
        fields = ["id", "name", "description", "seller", "is_favorite"]


class Stores(viewsets.ViewSet):
    """Request handlers for Products in the Bangazon Platform"""

    # Allow any user to GET, but only allow authenticated users to POST
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

    def create(self, request):
        """Handle POST operations for a Store"""
        customer = Customer.objects.get(user=request.auth.user)

        if hasattr(customer, "store"):
            # customer.store() raises an error if no store exists with a OneToOneField, so hasattr is safer than accessing customer.store directly to check if one exists
            return response.Response(
                {"message": "You already have a store."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        new_store = Store()
        new_store.name = request.data["name"]
        new_store.description = request.data["description"]
        new_store.customer = customer
        new_store.save()

        serializer = StoreSerializer(new_store, context={"request": request})

        return response.Response(serializer.data, status=status.HTTP_201_CREATED)

    def list(self, request):
        stores = Store.objects.all()
        serializer = StoreSerializer(stores, many=True, context={"request": request})
        return response.Response(serializer.data)

    def retrieve(self, request, pk=None):
        try:
            store = Store.objects.get(pk=pk)
            serializer = StoreSerializer(store, context={"request": request})
            return response.Response(serializer.data)
        except Store.DoesNotExist:
            return response.Response(
                {"message": "Store not found."}, status=status.HTTP_404_NOT_FOUND
            )
