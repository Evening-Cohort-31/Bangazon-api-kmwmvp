from django.http import HttpResponseServerError
from django.contrib.auth.models import User
from rest_framework import serializers, status
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet
from bangazonapi.models import Recommendation
from .product import Product
from .customer import Customer
from rest_framework.decorators import action


class RecommendationViewSet(ViewSet):

    def list(self, request):
        """Handle GET requests for all items

        Returns:
            Response -- JSON serialized array
        """
        
        try:
            recommender = Customer.objects.get(user=request.auth.user)
            recommendations = Recommendation.objects.filter(recommender = recommender)

            recommendations = RecommendationSerializer(
                recommendations, many=True, context={"request": request}
            )

            return Response(recommendations.data, status=status.HTTP_200_OK)
        
        except Exception as ex:
             return HttpResponseServerError(ex)
     
    @action(methods=['get'], detail=False)
    def recommended_to(self, request):

        if request.method == "GET":

            customer = Customer.objects.get(user=request.auth.user)
            recommendations = Recommendation.objects.filter(customer = customer)

            recommendations = RecommendationSerializer(
                recommendations, many=True, context={"request": request}
            )

            return Response(recommendations.data, status=status.HTTP_200_OK)
    
    

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



class UserSerializer(serializers.ModelSerializer):
    """ JSON serializer for customer profile """

    class Meta:
        model = User
        fields = ("first_name", "last_name", "email")



class CustomerSerializer(serializers.ModelSerializer):
    """ JSON serializer for recommendation customers """

    user = UserSerializer()

    class Meta:
        model = Customer
        fields = (
            "id",
            "user",
        )


class ProfileProductSerializer(serializers.ModelSerializer):
    """ JSON serializer for products liked by the user in their profile """

    class Meta:
        model = Product
        fields = (
            "id",
            "name",
            "price",
            "image_path",
        )



class RecommendationSerializer(serializers.ModelSerializer):
    """ JSON serializer for recommendations """

    customer = CustomerSerializer()
    product = ProfileProductSerializer()
    recommender = CustomerSerializer()

    class Meta:
        model = Recommendation
        fields = (
            "id",
            "product",
            "customer",
            "recommender",
        )