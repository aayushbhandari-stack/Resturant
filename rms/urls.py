from django.urls import path

from .views import (
    CategoryListCreateAPIView,
    CategoryDetailAPIView,

    FoodListCreateAPIView,
    FoodDetailAPIView,

    TableListCreateAPIView,
    TableDetailAPIView,

    cart_list,
    cart_detail,

    checkout,
    staff_login,

    OrderListCreateAPIView,
    OrderDetailAPIView,

    OrderStatusUpdateAPIView,

    PaymentListCreateAPIView,
    PaymentDetailAPIView,

    KitchenOrderAPIView,

    table_menu,
    kitchen_dashboard,
)


urlpatterns = [

    # =========================
    # CUSTOMER MENU
    # =========================

    path(
        "table/<int:table_number>/",
        table_menu,
        name="table-menu"
    ),


    # =========================
    # CATEGORY
    # =========================

    path(
        "categories/",
        CategoryListCreateAPIView.as_view(),
        name="category-list"
    ),

    path(
        "categories/<int:pk>/",
        CategoryDetailAPIView.as_view(),
        name="category-detail"
    ),


    # =========================
    # FOOD
    # =========================

    path(
        "foods/",
        FoodListCreateAPIView.as_view(),
        name="food-list"
    ),

    path(
        "foods/<int:pk>/",
        FoodDetailAPIView.as_view(),
        name="food-detail"
    ),


    # =========================
    # TABLES
    # =========================

    path(
        "tables/",
        TableListCreateAPIView.as_view(),
        name="table-list"
    ),

    path(
        "tables/<int:pk>/",
        TableDetailAPIView.as_view(),
        name="table-detail"
    ),


    # =========================
    # CART
    # =========================

    path(
        "cart/",
        cart_list,
        name="cart-list"
    ),

    path(
        "cart/<int:pk>/",
        cart_detail,
        name="cart-detail"
    ),


    # =========================
    # CHECKOUT
    # =========================

    path(
        "checkout/",
        checkout,
        name="checkout"
    ),


    # =========================
    # ORDERS
    # =========================

    path(
        "orders/",
        OrderListCreateAPIView.as_view(),
        name="order-list"
    ),

    path(
        "orders/<int:pk>/",
        OrderDetailAPIView.as_view(),
        name="order-detail"
    ),

    path(
        "orders/<int:pk>/status/",
        OrderStatusUpdateAPIView.as_view(),
        name="order-status-update"
    ),


    # =========================
    # PAYMENTS
    # =========================

    path(
        "payments/",
        PaymentListCreateAPIView.as_view(),
        name="payment-list"
    ),

    path(
        "payments/<int:pk>/",
        PaymentDetailAPIView.as_view(),
        name="payment-detail"
    ),


    # =========================
    # KITCHEN
    # =========================

    path(
        "kitchen/",
        kitchen_dashboard,
        name="kitchen-dashboard"
    ),

    path(
        "kitchen/orders/",
        KitchenOrderAPIView.as_view(),
        name="kitchen-orders"
    ),


    # =========================
    # STAFF LOGIN
    # =========================

    path(
        "staff/login/",
        staff_login,
        name="staff-login"
    ),
]
