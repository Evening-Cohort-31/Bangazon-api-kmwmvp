"""Tests for the payment type model"""

# Test are ran using the command "python manage.py test tests" in the terminal while in the project directory.

import datetime
import json
from rest_framework import status
from rest_framework.test import APITestCase


class PaymentTests(APITestCase):
    """Tests for the payment type model"""

    # Set up the test data (create a user and get a token)
    # This code was provided for us upon copying the repository
    def setUp(self) -> None:
        """
        Create a new account and create sample category
        """
        url = "/register"
        data = {
            "username": "valarie",
            "password": "Admin8*",
            "email": "valarie@example.com",
            "address": "1234 Hades Street",
            "phone_number": "555-1234",
            "first_name": "Valarie",
            "last_name": "Freeman",
        }
        response = self.client.post(url, data, format="json")
        json_response = json.loads(response.content)
        self.token = json_response["token"]
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    # Test that we can create a payment type for a customer
    # This code was provided for us upon copying the repository
    def test_create_payment_type(self):
        """
        Ensure we can add a payment type for a customer.
        """
        # Add product to order
        url = "/paymenttypes"
        data = {
            "merchant_name": "American Express",
            "account_number": "111-1111-1111",
            "expiration_date": "2024-12-31",
            "create_date": datetime.date.today(),
        }
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.token)
        response = self.client.post(url, data, format="json")
        json_response = json.loads(response.content)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(json_response["merchant_name"], "American Express")
        self.assertEqual(json_response["account_number"], "111-1111-1111")
        self.assertEqual(json_response["expiration_date"], "2024-12-31")
        self.assertEqual(json_response["create_date"], str(datetime.date.today()))

    # Test that we can delete a payment type for a customer
    # This section is the code for Ticket #6
    def test_delete_payment_type(self):
        """
        Ensure we can delete a payment type for a customer.
        """
        # Create a payment type that we will use to test the delete functionality.
        # Each test is responsible for creating its own data. setUp only registers a user.
        url = "/paymenttypes"
        # The data object must include every field the create method reads from request.data.
        # Those fields can be seen in views/paymenttype.py. The customer field is set
        # server-side from the token, so it is not included here.
        data = {
            "merchant_name": "American Express",
            "account_number": "111-1111-1111",
            "expiration_date": "2024-12-31",
            "create_date": datetime.date.today(),
        }

        # Attach the token from setUp to all future requests in this test.
        # Without this, the API will reject our requests with a 401 (Unauthorized).
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.token)

        # Make the POST request to create the payment type and store the response.
        response = self.client.post(url, data, format="json")
        json_response = json.loads(response.content)

        # Confirm the payment type was created before attempting to delete it.
        # A test that tries to delete something that was never created is not testing the right thing.
        # 201 (Created) confirms the payment type exists and that we have its ID in json_response.
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Build the URL for the specific payment type using its ID from the POST response.
        # Then make the DELETE request to remove it.
        url = f"/paymenttypes/{json_response['id']}"
        response = self.client.delete(url)

        # Assert that the delete operation returned 204 (No Content).
        # 204 means the server processed the request successfully and has no body to return,
        # which is the standard response for a successful DELETE.
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # Do a follow-up GET to verify the payment type is no longer accessible.
        # This confirms the full round-trip: not just that the DELETE request was accepted,
        # but that the resource is actually gone. We expect 404 (Not Found).
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
