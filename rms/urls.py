from django.urls import path

from .views import (
    CategoryListCreateAPIView,
    CategoryDetailAPIView,

    FoodListCreateAPIView,
    FoodDetailAPIView,

    TableListCreateAPIView,
    TableDetailAPIView,

    OrderListCreateAPIView,
    OrderDetailAPIView,

    OrderStatusUpdateAPIView,

    PaymentListCreateAPIView,
    PaymentDetailAPIView,

    KitchenOrderAPIView,
)
urlpatterns = [

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
        "payments/",
        PaymentListCreateAPIView.as_view(),
        name="payment-list"
    ),

    path(
        "payments/<int:pk>/",
        PaymentDetailAPIView.as_view(),
        name="payment-detail"
    ),
    
    path(
    "kitchen/orders/",
    KitchenOrderAPIView.as_view(),
    name="kitchen-orders"
),
    path(
    "orders/<int:pk>/status/",
    OrderStatusUpdateAPIView.as_view(),
    name="order-status-update"
),
]
