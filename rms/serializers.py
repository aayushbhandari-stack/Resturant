from rest_framework import serializers

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

class CategorySerializer(
    serializers.ModelSerializer
):

    class Meta:

        model = Category

        fields = [
            "id",
            "category_name",
            "created_at",
            "updated_at",
        ]

        read_only_fields = [
            "id",
            "created_at",
            "updated_at",
        ]


# =========================================================
# FOOD
# =========================================================

class FoodSerializer(
    serializers.ModelSerializer
):

    category_name = serializers.CharField(
        source="category.category_name",
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
            "image",
            "is_available",
            "updated_at",
        ]

        read_only_fields = [
            "id",
            "category_name",
            "updated_at",
        ]


# =========================================================
# TABLE
# =========================================================

class RestaurantTableSerializer(
    serializers.ModelSerializer
):

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
# CART
# =========================================================

class CartSerializer(
    serializers.ModelSerializer
):

    food_name = serializers.CharField(
        source="food.name",
        read_only=True
    )

    food_price = serializers.DecimalField(
        source="food.price",
        max_digits=10,
        decimal_places=2,
        read_only=True
    )

    subtotal = serializers.ReadOnlyField()

    class Meta:

        model = Cart

        fields = [
            "id",
            "session_id",
            "food",
            "food_name",
            "food_price",
            "quantity",
            "table",
            "special_instructions",
            "subtotal",
            "created_at",
        ]

        read_only_fields = [
            "id",
            "food_name",
            "food_price",
            "subtotal",
            "created_at",
        ]

    def validate_quantity(self, value):

        if value < 1:
            raise serializers.ValidationError(
                "Quantity must be at least 1."
            )

        return value


# =========================================================
# STAFF PROFILE
# =========================================================

class StaffProfileSerializer(
    serializers.ModelSerializer
):

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
# ORDER ITEM
# =========================================================

class OrderItemSerializer(
    serializers.ModelSerializer
):

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
            "food_name",
            "price",
            "subtotal",
        ]

    def validate_quantity(self, value):

        if value < 1:
            raise serializers.ValidationError(
                "Quantity must be at least 1."
            )

        return value


# =========================================================
# ORDER STATUS
# =========================================================

class OrderStatusUpdateSerializer(
    serializers.Serializer
):

    status = serializers.ChoiceField(
        choices=Order.STATUS_CHOICES
    )


# =========================================================
# ORDER
# =========================================================

class OrderSerializer(
    serializers.ModelSerializer
):

    items = OrderItemSerializer(
        many=True
    )

    total_amount = serializers.ReadOnlyField()

    table_number = serializers.IntegerField(
        source="table.table_number",
        read_only=True
    )

    class Meta:

        model = Order

        fields = [
            "id",
            "table",
            "table_number",
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
            "table_number",
        ]

    def validate_customer_phone(self, value):

        if not value:
            return value

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

        if value and not value.is_available:
            raise serializers.ValidationError(
                "This table is currently unavailable."
            )

        return value

    def create(self, validated_data):

        items_data = validated_data.pop(
            "items",
            []
        )

        order = Order.objects.create(
            **validated_data
        )

        for item_data in items_data:

            food = item_data["food"]

            OrderItem.objects.create(
                order=order,
                food=food,
                quantity=item_data["quantity"],
                price=food.price,
                special_instructions=
                    item_data.get(
                        "special_instructions",
                        ""
                    )
            )

        return order


# =========================================================
# PAYMENT
# =========================================================

class PaymentSerializer(
    serializers.ModelSerializer
):

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
