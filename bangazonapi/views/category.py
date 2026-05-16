"""View module for handling requests about product categories"""

from rest_framework import viewsets, status, serializers, permissions
from rest_framework.response import Response
from bangazonapi.models import ProductCategory


class ProductCategorySerializer(serializers.ModelSerializer):
    """JSON serializer for product category"""

    class Meta:
        model = ProductCategory
        fields = ["id", "name", "description", "parent_category"]


class ProductCategories(viewsets.ViewSet):
    """Categories for products"""

    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

    def create(self, request):
        """Handle POST operations

        Returns:
            Response -- JSON serialized product category instance
        """
        new_product_category = ProductCategory()
        new_product_category.name = request.data["name"]
        new_product_category.description = request.data["description"]
        if "parent_category" in request.data:
            new_product_category.parent_category_id = request.data["parent_category"]
        new_product_category.save()
        # TODO: add error handling for missing fields and invalid parent category
        serializer = ProductCategorySerializer(
            new_product_category, context={"request": request}
        )

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def retrieve(self, request, pk=None):
        """Handle GET requests for single category"""
        try:
            category = ProductCategory.objects.get(pk=pk)
            serializer = ProductCategorySerializer(
                category, context={"request": request}
            )
            return Response(serializer.data)
        except ProductCategory.DoesNotExist:
            return Response(
                {"message": "Category not found"}, status=status.HTTP_404_NOT_FOUND
            )

    def list(self, request):
        """Handle GET requests to ProductCategory resource"""
        product_categories = ProductCategory.objects.all()

        # Check for structured=true query parameter to return categories in a structured format
        structured = request.query_params.get("structured", "false").lower() == "true"
        if structured:
            # Build a dictionary to hold categories by their parent category
            structured_categories = {}
            for category in product_categories:
                # setdefault will create a new list for the parent_category_id if it doesn't exist
                structured_categories.setdefault(
                    category.parent_category_id, []
                ).append(category)

            # Function to recursively build the structured response
            def build_structure(parent_id):
                children = structured_categories.get(parent_id, [])
                return [
                    {
                        "id": child.id,
                        "name": child.name,
                        "description": child.description,
                        "parent_category": child.parent_category_id,
                        "children": build_structure(child.id),
                    }
                    for child in children
                ]

            # Start building the structure from the root categories (parent_id=None)
            structured_response = build_structure(None)
            return Response(structured_response)

        serializer = ProductCategorySerializer(
            product_categories, many=True, context={"request": request}
        )
        return Response(serializer.data)
