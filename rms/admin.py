from django.contrib import admin
from .models import (
    Category,
    Food,
    RestaurantTable,
    StaffProfile,
    Order,
    OrderItem,
    Payment,
)


# =========================
# CATEGORY
# =========================

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "Category_name",
        "created_at",
        "updated_at",
    )

    search_fields = ("Category_name",)


# =========================
# FOOD
# =========================

@admin.register(Food)
class FoodAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "category",
        "price",
        "updated_at",
    )

    list_filter = ("category",)

    search_fields = (
        "name",
        "category__Category_name",
    )


# =========================
# RESTAURANT TABLE
# =========================

@admin.register(RestaurantTable)
class RestaurantTableAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "table_number",
        "capacity",
        "is_available",
    )

    list_filter = ("is_available",)

    search_fields = ("table_number",)


# =========================
# STAFF PROFILE
# =========================

@admin.register(StaffProfile)
class StaffProfileAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "role",
    )

    list_filter = ("role",)

    search_fields = (
        "user__username",
    )


# =========================
# ORDER ITEM INLINE
# =========================

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0

    fields = (
        "food",
        "quantity",
        "price",
    )


# =========================
# ORDER
# =========================

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

    inlines = [
        OrderItemInline
    ]


# =========================
# PAYMENT
# =========================

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "order",
        "received_by",
        "amount",
        "method",
        "transaction_reference",
        "paid_at",
    )

    list_filter = (
        "method",
        "paid_at",
    )

    search_fields = (
        "order__id",
        "transaction_reference",
        "received_by__username",
    )