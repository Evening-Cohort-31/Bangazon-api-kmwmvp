from django.contrib.auth.models import User
from rest_framework import serializers, status
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet
from bangazonapi.models import Recommendation, Product, Customer



class RecommendationViewSet(ViewSet):

    def list(self, request):
        """Handle GET requests for recommendation objects

        Returns:
            Response -- JSON serialized array
        """
        
        #Uses query params to return recommendation objects filtered by customer recommending the product vs. customer the product was recommended to.
        try:
            customer = Customer.objects.get(user=request.auth.user)

            if request.query_params.get('recommended_to') == 'true':

                recommendations = Recommendation.objects.filter(customer = customer)
            else:
                recommendations = Recommendation.objects.filter(recommender = customer)
                
            recommendations = RecommendationSerializer(
                recommendations, many=True, context={"request": request}
            )

            return Response(recommendations.data, status=status.HTTP_200_OK)
        
        except Customer.DoesNotExist:
             return Response(
                {"message": "Customer profile not found for this user."},
                status=status.HTTP_404_NOT_FOUND,
            )

    
    def create(self, request, pk=None):
        """Handle POST operations for creating a new recommendation 

        Returns:
            Response -- JSON serialized instance
        """
            #Products are recommended by entering the username of the customer the current user wants to recommend the product to. If there is not customer with the username that was entered, a 404 error message is returned.
        try:
            customer = Customer.objects.get(user__username=request.data["username"])
            recommender = Customer.objects.get(user=request.auth.user)
            product = Product.objects.get(pk=request.data["product"])
            
            if Recommendation.objects.filter(customer=customer, product=product, recommender=recommender).exists():
                return Response({"message": "You have already recommended this product to this user."}, status=status.HTTP_400_BAD_REQUEST,)
            
            if customer == recommender:
                return Response({"message": "You cannot recommend a product to yourself."}, status=status.HTTP_400_BAD_REQUEST,)
            

            recommendation = Recommendation()
            recommendation.customer = customer
            recommendation.product = product
            recommendation.recommender = recommender

        
            recommendation.save()
            serializer = RecommendationSerializer(recommendation)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        except Customer.DoesNotExist:
            return Response({"message": "A customer with this username does not exist"}, status=status.HTTP_404_NOT_FOUND)
        
        except Product.DoesNotExist:
            return Response({"message": "The requested product does not exist."}, status=status.HTTP_404_NOT_FOUND)
        



class UserSerializer(serializers.ModelSerializer):
    """ JSON serializer for customer profile """

    class Meta:
        model = User
        fields = ("username", "first_name", "last_name", "email")



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
    """ JSON serializer for products listed on a user's profile """

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