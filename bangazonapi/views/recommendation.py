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


class RecommendationSerializer(serializers.ModelSerializer):
    """JSON serializer"""

    class Meta:
        model = Recommendation
        fields = ( 'id', 'customer', 'product', 'recommender' )