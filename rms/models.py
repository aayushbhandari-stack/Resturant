from django.db import models
from django.conf import settings
from decimal import Decimal
from django.core.validators import MinValueValidator
# Create your models here.

class Category (models.Model) :
    Category_name = models.CharField(max_length=100,)
    created_at = models.DateTimeField(auto_now_add=True,null=True,blank=True)
    updated_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.Category_name
    
class Food(models.Model):
    name = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.ForeignKey(Category,on_delete=models.CASCADE,related_name="foods")
    updated_at = models.DateTimeField(auto_now=True)    
    def __str__(self):
        return self.name
    

class RestaurantTable(models.Model):
    table_number = models.PositiveIntegerField(unique=True)
    capacity = models.PositiveIntegerField(default=4)
    is_available = models.BooleanField(default=True)

    def __str__(self):
        return f"Table {self.table_number}"
    
class RestaurantTable(models.Model):
    table_number = models.PositiveIntegerField(unique=True)
    capacity = models.PositiveIntegerField(default=4)
    is_available = models.BooleanField(default=True)

    def __str__(self):
        return f"Table {self.table_number}"


class Cart(models.Model):
    session_id = models.CharField(max_length=100)

    food = models.ForeignKey(
        Food,
        on_delete=models.CASCADE,
        related_name="cart_items"
    )

    quantity = models.PositiveIntegerField(
        default=1,
        validators=[MinValueValidator(1)]
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

    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def subtotal(self):
        return self.food.price * self.quantity

    def __str__(self):
        return f"{self.food.name} x {self.quantity}"
    
    
class StaffProfile(models.Model):
    ROLE_CHOICES = [
        ("chef", "Chef"),
        ("waiter", "Waiter"),
        ("manager", "Manager"),
        ("reception", "Reception"),
    ]

    user = models.OneToOneField(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,related_name="staff_profile",null=False)
    role = models.CharField(max_length=20,choices=ROLE_CHOICES)

    def __str__(self):
        return f"{self.user.username} - {self.role}"

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

    PAYMENT_STATUS = [
        ("unpaid", "Unpaid"),
        ("paid", "Paid"),
        ]
    
    

    PAYMENT_METHODS = [
        ("cash", "Cash"),
        ("card", "Card"),
        ("online", "Online Payment"),
    ]
    
    table = models.ForeignKey(RestaurantTable,on_delete=models.PROTECT,related_name="orders",null=True)
    # Customer information
    customer_name = models.CharField(max_length=100,blank=False,null=True)
    customer_phone = models.CharField(max_length=10,blank=False,null=True)

    # Special instructions for the kitchen
    special_instructions = models.TextField(blank=True,null=True)
    status = models.CharField(max_length=20,choices=STATUS_CHOICES,default="pending")
    payment_status = models.CharField(max_length=20,choices=PAYMENT_STATUS,default="unpaid")
    created_at = models.DateTimeField(auto_now_add=True,null=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Order #{self.id} - Table {self.table.table_number}"

    @property
    def total_amount(self):
        return sum(
            item.subtotal
            for item in self.items.all()
        )
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
        validators=[MinValueValidator(1)]
    )

    price = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    special_instructions = models.TextField(
        blank=True,
        null=True
    )

    @property
    def subtotal(self):
        return self.price * self.quantity

    def __str__(self):
        return f"{self.food.name} x {self.quantity}"


class Payment(models.Model):

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
        choices=Order.PAYMENT_METHODS
    )

    transaction_reference = models.CharField(
        max_length=100,
        blank=True
    )

    paid_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Payment for Order #{self.order_id}"