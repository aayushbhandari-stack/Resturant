from rest_framework import serializers

from .models import (
    Category,
    Food,
    RestaurantTable,
    StaffProfile,
    Order,
    OrderItem,
    Payment,
)

class OrderStatusUpdateSerializer(serializers.Serializer):
    status = serializers.ChoiceField(
        choices=Order.STATUS_CHOICES
    )
# =========================================================
# CATEGORY SERIALIZER
# =========================================================

class CategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = Category

        fields = [
            "id",
            "Category_name",
            "created_at",
            "updated_at",
        ]

        read_only_fields = [
            "id",
            "created_at",
            "updated_at",
        ]


# =========================================================
# FOOD SERIALIZER
# =========================================================

class FoodSerializer(serializers.ModelSerializer):

    category_name = serializers.CharField(
        source="category.Category_name",
        read_only=True
    )

    class Meta:
        model = Food

        fields = [
            "id",
            "name",
            "price",
            "category",
            "category_name",
            "updated_at",
        ]

        read_only_fields = [
            "id",
            "updated_at",
            "category_name",
        ]


# =========================================================
# RESTAURANT TABLE SERIALIZER
# =========================================================

class RestaurantTableSerializer(serializers.ModelSerializer):

    class Meta:
        model = RestaurantTable

        fields = [
            "id",
            "table_number",
            "capacity",
            "is_available",
        ]

        read_only_fields = [
            "id",
        ]


# =========================================================
# STAFF PROFILE SERIALIZER
# =========================================================

class StaffProfileSerializer(serializers.ModelSerializer):

    username = serializers.CharField(
        source="user.username",
        read_only=True
    )

    class Meta:
        model = StaffProfile

        fields = [
            "id",
            "user",
            "username",
            "role",
        ]

        read_only_fields = [
            "id",
            "username",
        ]


# =========================================================
# ORDER ITEM SERIALIZER
# =========================================================

class OrderItemSerializer(serializers.ModelSerializer):

    food_name = serializers.CharField(
        source="food.name",
        read_only=True
    )

    subtotal = serializers.ReadOnlyField()

    class Meta:
        model = OrderItem

        fields = [
            "id",
            "food",
            "food_name",
            "quantity",
            "price",
            "special_instructions",
            "subtotal",
        ]

        read_only_fields = [
            "id",
            "price",
            "subtotal",
            "food_name",
        ]

    def validate_quantity(self, value):

        if value < 1:
            raise serializers.ValidationError(
                "Quantity must be at least 1."
            )

        return value


# =========================================================
# ORDER SERIALIZER
# =========================================================

class OrderSerializer(serializers.ModelSerializer):

    items = OrderItemSerializer(
        many=True
    )

    total_amount = serializers.ReadOnlyField()

    class Meta:
        model = Order

        fields = [
            "id",
            "table",
            "customer_name",
            "customer_phone",
            "special_instructions",
            "status",
            "payment_status",
            "items",
            "total_amount",
            "created_at",
            "updated_at",
        ]

        read_only_fields = [
            "id",
            "status",
            "payment_status",
            "total_amount",
            "created_at",
            "updated_at",
        ]

    def validate_customer_phone(self, value):

        if not value.isdigit():
            raise serializers.ValidationError(
                "Phone number must contain only numbers."
            )

        if len(value) != 10:
            raise serializers.ValidationError(
                "Phone number must contain exactly 10 digits."
            )

        return value

    def validate_table(self, value):

        if not value.is_available:
            raise serializers.ValidationError(
                "This table is currently unavailable."
            )

        return value

    def create(self, validated_data):

        # Get items from request
        items_data = validated_data.pop("items")

        # Create the order
        order = Order.objects.create(
            **validated_data
        )

        # Create every order item
        for item_data in items_data:

            food = item_data["food"]

            OrderItem.objects.create(
                order=order,
                food=food,

                # Quantity comes from customer
                quantity=item_data["quantity"],

                # Price MUST come from database
                price=food.price,

                special_instructions=
                    item_data.get(
                        "special_instructions"
                    )
            )

        return order


# =========================================================
# PAYMENT SERIALIZER
# =========================================================

class PaymentSerializer(serializers.ModelSerializer):

    order_total = serializers.DecimalField(
        source="order.total_amount",
        max_digits=10,
        decimal_places=2,
        read_only=True
    )

    received_by_username = serializers.CharField(
        source="received_by.username",
        read_only=True
    )

    class Meta:
        model = Payment

        fields = [
            "id",
            "order",
            "order_total",
            "received_by",
            "received_by_username",
            "amount",
            "method",
            "transaction_reference",
            "paid_at",
        ]

        read_only_fields = [
            "id",
            "order_total",
            "received_by",
            "received_by_username",
            "paid_at",
        ]