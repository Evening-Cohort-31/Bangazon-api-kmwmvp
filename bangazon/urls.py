from django.conf import settings
from django.urls import include, path
from django.conf.urls.static import static
from rest_framework import routers
from rest_framework.authtoken.views import obtain_auth_token
from bangazonapi.models import *
from bangazonapi.views import *
from bangazonapi.views.report import (
    completed_orders_report,
    pending_orders_report,
    inexpensive_products_report,
    expensive_products_report,
    favorite_sellers_report,
)

# pylint: disable=invalid-name
router = routers.DefaultRouter(trailing_slash=False)
router.register(r"products", ProductViewSet, "product")
router.register(r"productcategories", ProductCategories, "productcategory")
router.register(r"lineitems", LineItems, "orderproduct")
router.register(r"customers", Customers, "customer")
router.register(r"users", Users, "user")
router.register(r"orders", OrderViewSet, "order")
router.register(r"cart", CartViewSet, "cart")
router.register(r"paymenttypes", PaymentViewSet, "payment")
router.register(r"profile", ProfileViewSet, "profile")
router.register(r"stores", StoreViewSet, "store")
router.register(r"favorites", FavoriteViewSet, "favorite")
router.register(r"recommendations", RecommendationViewSet, "recommendation")


# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    path("", include(router.urls)),
    path("register", register_user),
    path("login", login_user),
    path("api-token-auth", obtain_auth_token),
    path("api-auth", include("rest_framework.urls", namespace="rest_framework")),
    path(
        "reports/completed_orders",
        completed_orders_report,
        name="completed_orders",
    ),
    path("reports/pending_orders", pending_orders_report, name="pending_orders"),
    path(
        "reports/inexpensive_products",
        inexpensive_products_report,
        name="inexpensive_products",
    ),
    path(
        "reports/expensive_products",
        expensive_products_report,
        name="expensive_products",
    ),
    path("reports/favoritesellers", favorite_sellers_report, name="favorite_sellers"),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
