from django.urls import path

from . import views


urlpatterns = [

    # ========================================================
    # CUSTOMER
    # ========================================================

    path(
    "order/table/<uuid:qr_token>/",
    views.qr_table_menu,
    name="qr_table_menu",
),

    path(
        "",
        views.home,
        name="home",
    ),

    path(
        "table/<int:table_number>/",
        views.table_menu,
        name="table_menu",
    ),

    path(
        "cart/",
        views.cart,
        name="cart",
    ),

    path(
        "cart/add/<int:food_id>/",
        views.add_to_cart,
        name="add_to_cart",
    ),

    path(
        "checkout/",
        views.checkout,
        name="checkout",
    ),

    path(
        "place-order/",
        views.place_order,
        name="place_order",
    ),

    # ========================================================
    # LOGIN
    # ========================================================

    path(
        "login/",
        views.login_view,
        name="login",
    ),

    path(
        "logout/",
        views.logout_view,
        name="logout",
    ),

    # ========================================================
    # MANAGER DASHBOARD
    # ========================================================

    path(
        "manager/",
        views.manager_dashboard,
        name="manager_dashboard",
    ),

    # ========================================================
    # MANAGER STAFF
    # ========================================================

    path(
        "manager/staff/",
        views.staff_list,
        name="staff_list",
    ),

    # ========================================================
    # MANAGER FOOD
    # ========================================================

    path(
        "manager/food/",
        views.manager_food_list,
        name="manager_food_list",
    ),

    path(
        "manager/food/create/",
        views.manager_food_create,
        name="manager_food_create",
    ),

    path(
        "manager/food/edit/<int:food_id>/",
        views.manager_food_edit,
        name="manager_food_edit",
    ),

    path(
        "manager/food/delete/<int:food_id>/",
        views.manager_food_delete,
        name="manager_food_delete",
    ),

    # ========================================================
    # MANAGER CATEGORY
    # ========================================================

    path(
        "manager/categories/",
        views.manager_category_list,
        name="manager_category_list",
    ),

    path(
        "manager/categories/create/",
        views.manager_category_create,
        name="manager_category_create",
    ),

    path(
        "manager/categories/edit/<int:category_id>/",
        views.manager_category_edit,
        name="manager_category_edit",
    ),

    path(
        "manager/categories/delete/<int:category_id>/",
        views.manager_category_delete,
        name="manager_category_delete",
    ),

    # ========================================================
    # MANAGER ORDERS
    # ========================================================

    path(
        "manager/orders/",
        views.manager_order_list,
        name="manager_order_list",
    ),

    path(
        "manager/orders/<int:order_id>/status/",
        views.manager_order_status,
        name="manager_order_status",
    ),

    # ========================================================
    # MANAGER TABLES
    # ========================================================

    path(
        "manager/tables/",
        views.manager_table_list,
        name="manager_table_list",
    ),

    path(
        "manager/tables/create/",
        views.manager_table_create,
        name="manager_table_create",
    ),

    path(
        "manager/tables/edit/<int:table_id>/",
        views.manager_table_edit,
        name="manager_table_edit",
    ),

    path(
        "manager/tables/delete/<int:table_id>/",
        views.manager_table_delete,
        name="manager_table_delete",
    ),
    
    path(
    "manager/tables/<int:table_id>/qr/",
    views.manager_table_qr,
    name="manager_table_qr",
),


    # ========================================================
    # RECEPTION
    # ========================================================

    path(
        "reception/",
        views.reception_dashboard,
        name="reception_dashboard",
    ),
    path("reception/orders/", views.reception_order_list, name="reception_order_list"),
    path(
    "reception/payments/",
    views.reception_payment_list,
    name="reception_payment_list",
),
    path(
    "reception/customers/",
    views.reception_customer_list,
    name="reception_customer_list",
),
    path(
    "reception/tables/",
    views.reception_table_list,
    name="reception_table_list",
),  
    path(
    "api/reception/dashboard/",
    views.reception_dashboard_api,
    name="reception-dashboard-api",
),


    # ========================================================
    # WAITER
    # ========================================================

    path(
        "waiter/",
        views.waiter_dashboard,
        name="waiter_dashboard",
    ),

    # ========================================================
    # KITCHEN
    # ========================================================

    path(
        "kitchen/",
        views.kitchen_dashboard,
        name="kitchen_dashboard",
    ),

    # ========================================================
    # CATEGORY API
    # ========================================================

    path(
        "api/categories/",
        views.CategoryListCreateAPIView.as_view(),
        name="category-list",
    ),

    path(
        "api/categories/<int:pk>/",
        views.CategoryDetailAPIView.as_view(),
        name="category-detail",
    ),

    # ========================================================
    # FOOD API
    # ========================================================

    path(
        "api/foods/",
        views.FoodListCreateAPIView.as_view(),
        name="food-list",
    ),

    path(
        "api/foods/<int:pk>/",
        views.FoodDetailAPIView.as_view(),
        name="food-detail",
    ),

    # ========================================================
    # TABLE API
    # ========================================================

    path(
        "api/tables/",
        views.TableListCreateAPIView.as_view(),
        name="table-list",
    ),

    path(
        "api/tables/<int:pk>/",
        views.TableDetailAPIView.as_view(),
        name="table-detail",
    ),

    # ========================================================
    # CART API
    # ========================================================

    path(
        "api/cart/",
        views.cart_list,
        name="cart-list",
    ),

    path(
        "api/cart/<int:pk>/",
        views.cart_detail,
        name="cart-detail",
    ),

    # ========================================================
    # ORDER API
    # ========================================================

    path(
        "api/orders/",
        views.OrderListCreateAPIView.as_view(),
        name="order-list",
    ),

    path(
        "api/orders/<int:pk>/",
        views.OrderDetailAPIView.as_view(),
        name="order-detail",
    ),

    path(
        "api/orders/<int:pk>/status/",
        views.OrderStatusUpdateAPIView.as_view(),
        name="order-status-update",
    ),

    # ========================================================
    # PAYMENT API
    # ========================================================

    path(
        "api/payments/",
        views.PaymentListCreateAPIView.as_view(),
        name="payment-list",
    ),

    path(
        "api/payments/<int:pk>/",
        views.PaymentDetailAPIView.as_view(),
        name="payment-detail",
    ),

    # ========================================================
    # STAFF LOGIN API
    # ========================================================

    path(
        "api/staff/login/",
        views.staff_login,
        name="staff-login",
    ),

    # ========================================================
    # KITCHEN API
    # ========================================================

    path(
        "api/kitchen/orders/",
        views.KitchenOrderAPIView.as_view(),
        name="kitchen-orders",
    ),

    # ========================================================
    # STAFF ORDERS API
    # ========================================================

    path(
        "api/staff/orders/",
        views.StaffOrderAPIView.as_view(),
        name="staff-orders",
    ),
]
