"""Tests for Cart model and API endpoints."""

# Test are ran using the command "python manage.py test tests" in the terminal while in the project directory.

import json
from rest_framework import status
from rest_framework.test import APITestCase
from bangazonapi.models import Cart


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

    def test_create_cart_for_new_user(self):
        """
        Ensure a new user has an empty cart.
        """
        # Create a new user since cart is created when a new user is created
        url = "/register"
        data = {
            "username": "jane",
            "password": "Admin8*",
            "email": "jane@doe.com",
            "address": "123 Main St",
            "phone_number": "555-1234",
            "first_name": "Jane",
            "last_name": "Doe",
        }
        response = self.client.post(url, data, format="json")
        json_response = json.loads(response.content)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("token", json_response)
        token = json_response["token"]
        # See if cart was created for the new user
        url = "/cart"
        self.client.credentials(HTTP_AUTHORIZATION="Token " + token)
        response = self.client.get(url, None, format="json")
        json_response = json.loads(response.content)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(json_response["size"], 0)
        self.assertEqual(len(json_response["lineitems"]), 0)
        self.assertEqual(json_response["total"], 0.00)
        self.assertEqual(json_response["customer"], 2)

    def test_cart_operations_do_not_create_duplicate_carts(self):
        """Ensure repeated cart access keeps one cart per customer."""
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.token)

        self.client.get("/cart")
        self.client.get("/cart")
        self.client.post("/cart", {"product_id": 1}, format="json")
        response = self.client.delete("/cart/delete_all")

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Cart.objects.count(), 1)
