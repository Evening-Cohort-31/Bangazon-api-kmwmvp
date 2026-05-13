"""Register user"""

import json

# Import transaction management tools from Django to handle atomic database operations
from django.db import IntegrityError, transaction
from django.http import HttpResponse, HttpResponseNotAllowed
from django.contrib.auth import authenticate, get_user_model
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
from rest_framework.authtoken.models import Token
from bangazonapi.models import Customer

User = get_user_model()


@csrf_exempt
def login_user(request):
    """Handles the authentication of a user

    Method arguments:
      request -- The full HTTP request object
    """

    # If the request is a HTTP POST, process the request and login the user
    if request.method == "POST":

        req_body = json.loads(request.body.decode())

        # Validate that the required fields are included in the request body
        required_fields = ["username", "password"]

        for field in required_fields:
            if field not in req_body:
                return HttpResponse(
                    f"Missing required field: {field}",
                    status=status.HTTP_400_BAD_REQUEST,
                )

        # Use the built-in authenticate method to verify
        name = req_body["username"]
        pass_word = req_body["password"]
        authenticated_user = authenticate(username=name, password=pass_word)

        # If authentication was successful, respond with their token
        if authenticated_user is not None:
            token = Token.objects.get(user=authenticated_user)
            data = json.dumps(
                {"valid": True, "token": token.key, "id": authenticated_user.id}
            )
            return HttpResponse(data, content_type="application/json")

        else:
            # Bad login details were provided. So we can't log the user in.
            data = json.dumps({"valid": False})
            return HttpResponse(data, content_type="application/json")
    else:
        return HttpResponseNotAllowed(permitted_methods=["POST"])


@csrf_exempt
def register_user(request):
    """Handles the creation of a new user for authentication

    Method arguments:
      request -- The full HTTP request object
    """

    # If the request is a HTTP POST, process the request and login the user
    if request.method == "POST":

        # Load the JSON string of the request body into a dict
        req_body = json.loads(request.body.decode())

        # Validate that the required fields are included in the request body
        required_fields = ["username", "email", "password", "first_name", "last_name"]

        # Exit early if any required field is missing from the request body
        for field in required_fields:
            if field not in req_body:
                return HttpResponse(
                    f"Missing required field: {field}",
                    status=status.HTTP_400_BAD_REQUEST,
                )
        try:

            # Use a transaction to ensure that the user and customer records are created together
            with transaction.atomic():
                # Create a new user by invoking the `create_user` helper method
                # on Django's built-in User model
                new_user = User.objects.create_user(
                    username=req_body["username"],
                    email=req_body["email"],
                    password=req_body["password"],
                    first_name=req_body["first_name"],
                    last_name=req_body["last_name"],
                )

                # Create a new customer record for the new user
                # If phone_number and address are not provided in the request body, default to empty strings
                req_body.setdefault("phone_number", "")
                req_body.setdefault("address", "")

                Customer.objects.create(
                    phone_number=req_body["phone_number"],
                    address=req_body["address"],
                    user=new_user,
                )

                # Use the REST Framework's token generator on the new user account
                token = Token.objects.create(user=new_user)

            # Return the token to the client
            data = json.dumps({"token": token.key, "id": new_user.id})

            return HttpResponse(
                data, content_type="application/json", status=status.HTTP_201_CREATED
            )

        except IntegrityError:
            return HttpResponse(
                "Username already exists. Please choose a different username.",
                status=status.HTTP_409_CONFLICT,
            )

    else:
        return HttpResponseNotAllowed(permitted_methods=["POST"])
