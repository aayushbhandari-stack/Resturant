from decimal import Decimal
import uuid
from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models


# =========================================================
# CATEGORY
# =========================================================

class Category(models.Model):

    category_name = models.CharField(
        max_length=100
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    def __str__(self):
        return self.category_name


# =========================================================
# FOOD
# =========================================================

class Food(models.Model):

    name = models.CharField(
        max_length=200
    )

    price = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name="foods"
    )

    image = models.ImageField(
        upload_to="foods/",
        blank=True,
        null=True
    )

    is_available = models.BooleanField(
        default=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    def __str__(self):
        return self.name


# =========================================================
# RESTAURANT TABLE
# =========================================================

# ============================================================
# TABLE CREATE
# ============================================================
# =========================================================
# RESTAURANT TABLE
# =========================================================
class RestaurantTable(models.Model):

    table_number = models.PositiveIntegerField(
        unique=True
    )

    qr_token = models.UUIDField(
        default=uuid.uuid4,
        unique=True,
        editable=False
    )

    is_available = models.BooleanField(
        default=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True,null=True,blank=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    def __str__(self):
        return f"Table {self.table_number}"




# =========================================================
# CART
# =========================================================

class Cart(models.Model):

    session_id = models.CharField(
        max_length=100
    )

    food = models.ForeignKey(
        Food,
        on_delete=models.CASCADE,
        related_name="cart_items"
    )

    quantity = models.PositiveIntegerField(
        default=1,
        validators=[
            MinValueValidator(1)
        ]
    )

    table = models.ForeignKey(
        RestaurantTable,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="cart_items"
    )

    special_instructions = models.TextField(
        blank=True,
        null=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    @property
    def subtotal(self):
        return self.food.price * self.quantity

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=[
                    "session_id",
                    "food"
                ],
                name="unique_cart_food_per_session"
            )
        ]

    def __str__(self):
        return f"{self.food.name} x {self.quantity}"


# =========================================================
# STAFF PROFILE
# =========================================================

class StaffProfile(models.Model):

    ROLE_CHOICES = [
        ("chef", "Chef"),
        ("waiter", "Waiter"),
        ("manager", "Manager"),
        ("reception", "Reception"),
    ]

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="staff_profile"
    )

    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES
    )

    def __str__(self):
        return f"{self.user.username} - {self.role}"


# =========================================================
# ORDER
# =========================================================

class Order(models.Model):

    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("confirmed", "Confirmed"),
        ("preparing", "Preparing"),
        ("ready", "Ready"),
        ("served", "Served"),
        ("completed", "Completed"),
        ("cancelled", "Cancelled"),
    ]

    PAYMENT_STATUS_CHOICES = [
        ("unpaid", "Unpaid"),
        ("paid", "Paid"),
    ]

    table = models.ForeignKey(
        RestaurantTable,
        on_delete=models.PROTECT,
        related_name="orders",
        null=True,
        blank=True
    )

    customer_name = models.CharField(
        max_length=100,
        blank=True
    )

    customer_phone = models.CharField(
        max_length=20,
        blank=True
    )

    special_instructions = models.TextField(
        blank=True
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="pending"
    )

    payment_status = models.CharField(
        max_length=20,
        choices=PAYMENT_STATUS_CHOICES,
        default="unpaid"
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    def __str__(self):
        if self.table:
            return (
                f"Order #{self.id} - "
                f"Table {self.table.table_number}"
            )

        return f"Order #{self.id}"

    @property
    def total_amount(self):
        return sum(
            (
                item.subtotal
                for item in self.items.all()
            ),
            Decimal("0.00")
        )


# =========================================================
# ORDER ITEM
# =========================================================

class OrderItem(models.Model):

    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="items"
    )

    food = models.ForeignKey(
        Food,
        on_delete=models.PROTECT,
        related_name="order_items"
    )

    quantity = models.PositiveIntegerField(
        validators=[
            MinValueValidator(1)
        ]
    )

    price = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    special_instructions = models.TextField(
        blank=True
    )

    @property
    def subtotal(self):
        return self.price * self.quantity

    def __str__(self):
        return (
            f"{self.food.name} x "
            f"{self.quantity}"
        )


# =========================================================
# PAYMENT
# =========================================================

class Payment(models.Model):

    PAYMENT_METHODS = [
        ("cash", "Cash"),
        ("card", "Card"),
        ("online", "Online Payment"),
    ]

    order = models.OneToOneField(
        Order,
        on_delete=models.PROTECT,
        related_name="payment"
    )

    received_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="received_payments"
    )

    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    method = models.CharField(
        max_length=20,
        choices=PAYMENT_METHODS
    )

    transaction_reference = models.CharField(
        max_length=100,
        blank=True
    )

    paid_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return (
            f"Payment for Order "
            f"#{self.order_id}"
        )
