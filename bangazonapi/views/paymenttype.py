"""View module for handling requests about customer payment types"""

from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework import serializers
from rest_framework import status
from bangazonapi.models import Payment, Customer
from bangazonapi.validators import CreditCardValidator, CreditCardDateValidator


class PaymentSerializer(serializers.ModelSerializer):
    """JSON serializer for Payment

    Arguments:
        serializers
    """

    class Meta:
        model = Payment
        fields = (
            "id",
            "merchant_name",
            "account_number",
            "expiration_date",
            "create_date",
        )

    def validate_account_number(self, value):
        """Validator for credit card number format 13 to 19 digits"""
        try:
            CreditCardValidator().validate(value)
        except DjangoValidationError as e:
            raise serializers.ValidationError(e.messages)
        return value

    def validate_expiration_date(self, value):
        """Validator for credit card expiration date format MM/YY"""
        try:
            CreditCardDateValidator().validate(value)
        except DjangoValidationError as e:
            raise serializers.ValidationError(e.messages)
        return value


class PaymentViewSet(ViewSet):

    def create(self, request):
        """Handle POST operations

        Returns:
            Response -- JSON serialized payment instance
        """
        serializer = PaymentSerializer(data=request.data)

        # Validate the incoming data and raise an exception if any is invalid.
        # Validation errors are propagated as a 400 Bad Request response
        serializer.is_valid(raise_exception=True)

        try:
            customer = Customer.objects.get(user=request.auth.user)
            serializer.save(customer=customer)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        except Customer.DoesNotExist:
            return Response(
                {"message": "You cannot add a payment method for this account"},
                status=status.HTTP_403_FORBIDDEN,
            )

    def retrieve(self, request, pk=None):
        """Handle GET requests for single payment type

        Returns:
            Response -- JSON serialized payment_type instance
        """
        try:
            payment_type = Payment.objects.get(pk=pk)
            serializer = PaymentSerializer(payment_type, context={"request": request})
            return Response(serializer.data)

        except Payment.DoesNotExist as ex:
            return Response({"message": ex.args[0]}, status=status.HTTP_404_NOT_FOUND)

        except Exception as ex:
            return Response(
                {"message": ex.args[0]}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def destroy(self, request, pk=None):
        """Handle DELETE requests for a single payment type

        Returns:
            Response -- 200, 404, or 500 status code
        """
        try:
            payment = Payment.objects.get(pk=pk)
            payment.delete()

            return Response({}, status=status.HTTP_204_NO_CONTENT)

        except Payment.DoesNotExist as ex:
            return Response({"message": ex.args[0]}, status=status.HTTP_404_NOT_FOUND)

        except Exception as ex:
            return Response(
                {"message": ex.args[0]}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def list(self, request):
        """Handle GET requests to payment type resource"""
        customer = Customer.objects.get(user=request.auth.user)
        payment_types = Payment.objects.filter(customer=customer)

        serializer = PaymentSerializer(
            payment_types, many=True, context={"request": request}
        )
        return Response(serializer.data)
