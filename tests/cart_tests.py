"""Tests for Cart model and API endpoints."""

# Test are ran using the command "python manage.py test tests" in the terminal while in the project directory.

import json
from rest_framework import status
from rest_framework.test import APITestCase


class CartTests(APITestCase):
    def setUp(self) -> None:
        """
        Create a new account and create sample category
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
            "category": [category_id],
            "location": "Pittsburgh",
        }
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.token)
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_add_product_to_cart(self):
        """
        Ensure we can add a product to a cart.
        """
        # Add product to cart
        url = "/cart"
        data = {"product_id": 1}
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.token)
        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Get cart and verify product was added
        url = "/cart"
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.token)
        response = self.client.get(url, None, format="json")
        json_response = json.loads(response.content)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(json_response["id"], 1)
        self.assertEqual(json_response["size"], 1)
        self.assertEqual(len(json_response["lineitems"]), 1)

    def test_remove_product_from_cart(self):
        """
        Ensure we can remove a product from a cart.
        """
        # Add product to cart
        url = "/cart"
        data = {"product_id": 1}
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.token)
        response = self.client.post(url, data, format="json")
        json_response = json.loads(response.content)

        # Verify product was added to cart before attempting to remove it
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Remove product from cart
        url = f"/cart/{json_response['id']}"
        response = self.client.delete(url)

        # Verify product was removed from cart
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # Get cart and verify product was removed
        url = "/cart"
        response = self.client.get(url, None, format="json")
        json_response = json.loads(response.content)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(json_response["size"], 0)
        self.assertEqual(len(json_response["lineitems"]), 0)

    # TODO: Complete order by adding payment type
