
from rest_framework import (
    serializers,
    status,
    permissions,
    viewsets,
    response,
)

from bangazonapi.models import Customer, Store

class StoreSerializer(serializers.ModelSerializer):
     """JSON serializer for STORE SERIALIZER summary"""
     class Meta:
          model = Store
          fields = ["id", "name", "description", "customer_id"]

class Stores(viewsets.ViewSet):
    """Request handlers for Products in the Bangazon Platform"""
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

    def create(self, request):
       
        new_store = Store()
        new_store.name = request.data["name"]
        new_store.description = request.data["description"]
        
        customer = Customer.objects.get(user=request.auth.user)
        new_store.customer = customer

        new_store.save()



        serializer = StoreSerializer(new_store, context={"request": request})

        return response.Response(serializer.data, status=status.HTTP_201_CREATED)

    def list(self, request):
        stores = Store.objects.all()
        serializer = StoreSerializer(
            stores, many=True, context={"request": request}
        )
        return response.Response(serializer.data)