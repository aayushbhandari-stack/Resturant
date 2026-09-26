from django.contrib import admin

from .models import (
    Category,
    Food,
    RestaurantTable,
    Cart,
    StaffProfile,
    Order,
    OrderItem,
    Payment,
)


# =========================================================
# CATEGORY
# =========================================================

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "category_name",
        "created_at",
        "updated_at",
    )

    search_fields = (
        "category_name",
    )

    ordering = (
        "category_name",
    )


# =========================================================
# FOOD
# =========================================================

@admin.register(Food)
class FoodAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "name",
        "category",
        "price",
        "is_available",
        "updated_at",
    )

    list_filter = (
        "category",
        "is_available",
    )

    search_fields = (
        "name",
        "category__category_name",
    )

    ordering = (
        "name",
    )


# =========================================================
# RESTAURANT TABLE
# =========================================================

@admin.register(RestaurantTable)
class RestaurantTableAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "table_number",
        "is_available",
    )

    list_filter = (
        "is_available",
    )

    ordering = (
        "table_number",
    )


# =========================================================
# CART
# =========================================================

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "session_id",
        "food",
        "quantity",
        "table",
        "created_at",
    )

    search_fields = (
        "session_id",
        "food__name",
    )

    list_filter = (
        "created_at",
    )


# =========================================================
# STAFF PROFILE
# =========================================================

@admin.register(StaffProfile)
class StaffProfileAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "user",
        "role",
    )

    list_filter = (
        "role",
    )

    search_fields = (
        "user__username",
    )


# =========================================================
# ORDER ITEM INLINE
# =========================================================

class OrderItemInline(
    admin.TabularInline
):

    model = OrderItem

    extra = 0

    readonly_fields = (
        "price",
        "subtotal",
    )


# =========================================================
# ORDER
# =========================================================

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "table",
        "customer_name",
        "customer_phone",
        "status",
        "payment_status",
        "created_at",
    )

    list_filter = (
        "status",
        "payment_status",
        "created_at",
    )

    search_fields = (
        "customer_name",
        "customer_phone",
    )

    ordering = (
        "-created_at",
    )

    inlines = [
        OrderItemInline,
    ]


# =========================================================
# ORDER ITEM
# =========================================================

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "order",
        "food",
        "quantity",
        "price",
    )

    search_fields = (
        "food__name",
    )


# =========================================================
# PAYMENT
# =========================================================

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "order",
        "amount",
        "method",
        "received_by",
        "paid_at",
    )

    list_filter = (
        "method",
        "paid_at",
    )

    search_fields = (
        "order__id",
        "received_by__username",
        "transaction_reference",
    )
