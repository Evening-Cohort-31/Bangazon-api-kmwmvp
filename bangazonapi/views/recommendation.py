from django.http import HttpResponseServerError
from rest_framework import serializers, status
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet
from bangazonapi.models import Recommendation
from .product import Product
from .customer import Customer


class RecommendationViewSet(ViewSet):

    def list(self, request):
        """Handle GET requests for all items

        Returns:
            Response -- JSON serialized array
        """
        try:
            recommendations = Recommendation.objects.all()
            serializer = RecommendationSerializer(recommendations, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as ex:
            return HttpResponseServerError(ex)
    
    def create(self, request, pk=None):
        """Handle POST operations

        Returns:
            Response -- JSON serialized instance
        """

        try:
            customer = Customer.objects.get(user__username=request.data["username"])
        except Customer.DoesNotExist:
            return Response({"reason": "User not found"}, status=status.HTTP_404_NOT_FOUND)

        recommendation = Recommendation()
        recommendation.customer = customer
        recommendation.product = Product.objects.get(pk=request.data["product"])
        recommendation.recommender = Customer.objects.get(user=request.auth.user)

        try:
            recommendation.save()
            serializer = RecommendationSerializer(recommendation)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as ex:
            return Response({"reason": ex.args[0]}, status=status.HTTP_400_BAD_REQUEST)


class RecommendationSerializer(serializers.ModelSerializer):
    """JSON serializer"""

    class Meta:
        model = Recommendation
        fields = ( 'id', 'customer', 'product', 'recommender' )