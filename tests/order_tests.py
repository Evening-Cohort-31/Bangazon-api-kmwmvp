"""Tests for Order model and API endpoints."""

# Test are ran using the command "python manage.py test tests" in the terminal while in the project directory.

import json
from rest_framework import status
from rest_framework.test import APITestCase


class OrderTests(APITestCase):
    def setUp(self) -> None:
        """
        Create a new account,
        create a product to buy and it's category,
        then add the product to the cart,
        and then lastly create a new payment method to use for checkout
        """

        url = "/register"
        data = {
            "username": "steve",
            "password": "Admin8*",
            "email": "steve@stevebrownlee.com",
            "address": "100 Infinity Way",
            "phone_number": "555-1212",
            "first_name": "Steve",
            "last_name": "Brownlee",
        }
        response = self.client.post(url, data, format="json")
        json_response = json.loads(response.content)
        self.token = json_response["token"]
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Create a product category
        url = "/productcategories"
        data = {
            "name": "Sporting Goods",
            "description": "All the sporting goods you need",
            "parent_category": None,
        }
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.token)
        response = self.client.post(url, data, format="json")
        json_response = json.loads(response.content)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(json_response["name"], "Sporting Goods")
        self.assertEqual(
            json_response["description"], "All the sporting goods you need"
        )
        self.assertEqual(json_response["parent_category"], None)

        category_id = json_response["id"]

        # Create a product
        url = "/products"
        data = {
            "name": "Kite",
            "price": "14.99",
            "quantity": 60,
            "description": "It flies high",
            "category_ids": [category_id],
            "location": "Pittsburgh",
        }
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.token)
        response = self.client.post(url, data, format="json")
        json_response = json.loads(response.content)
        # Verify entire product creation process was successful before attempting to add product to cart
        self.assertEqual(json_response["name"], "Kite")
        self.assertEqual(json_response["price"], "14.99")
        self.assertEqual(json_response["quantity"], 60)
        self.assertEqual(json_response["description"], "It flies high")
        self.assertEqual(json_response["categories"][0]["id"], category_id)
        self.assertEqual(json_response["categories"][0]["name"], "Sporting Goods")
        self.assertEqual(json_response["location"], "Pittsburgh")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Add product to cart
        url = "/cart"
        data = {
            "product_id": json_response["id"],
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Create a payment type
        url = "/paymenttypes"
        data = {
            "merchant_name": "Visa",
            "account_number": "123456789",
            "expiration_date": "2025-12-31",
        }
        response = self.client.post(url, data, format="json")
        json_response = json.loads(response.content)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(json_response["id"], 1)
        self.assertEqual(json_response["merchant_name"], "Visa")
        self.assertEqual(json_response["account_number"], "123456789")
        self.assertEqual(json_response["expiration_date"], "2025-12-31")

    def test_create_order(self):
        """
        Ensure we can create a new order which entails taking the cart and converting it to an order with line items, and that the product quantity is updated accordingly.
        """
        url = "/orders"
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.token)
        data = {"payment_type": 1}
        response = self.client.post(url, data, format="json")
        json_response = json.loads(response.content)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(json_response["id"], 1)
        self.assertEqual(json_response["payment_type"]["id"], 1)
        self.assertEqual(json_response["payment_type"]["merchant_name"], "Visa")
        self.assertEqual(json_response["payment_type"]["account_number"], "123456789")
        self.assertEqual(json_response["payment_type"]["expiration_date"], "2025-12-31")
        self.assertEqual(json_response["customer"], 1)
        self.assertEqual(json_response["lineitems"][0]["product"]["name"], "Kite")
        self.assertEqual(json_response["lineitems"][0]["product"]["price"], "14.99")
        self.assertEqual(
            json_response["lineitems"][0]["product"]["description"], "It flies high"
        )
        self.assertEqual(json_response["total"], 14.99)
        self.assertEqual(json_response["size"], 1)
