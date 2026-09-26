from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from rms.models import (
    category,
    Food,
    RestaurantTable,
    Cart,
    Order,
    OrderItem,
)

def place_order(request):

    if request.method != "POST":
        return redirect("checkout")

    # Create session if needed
    if not request.session.session_key:
        request.session.create()

    session_id = request.session.session_key

    # Get cart items
    cart_items = Cart.objects.filter(
        session_id=session_id
    ).select_related("food")

    # If cart is empty
    if not cart_items.exists():
        return redirect("cart")

    # Get customer information
    customer_name = request.POST.get("customer_name")
    customer_phone = request.POST.get("customer_phone")
    table_id = request.POST.get("table")
    special_instructions = request.POST.get(
        "special_instructions",
        ""
    )

    # Get selected table
    table = get_object_or_404(
        RestaurantTable,
        id=table_id,
        is_available=True
    )

    # Create order
    order = Order.objects.create(
        table=table,
        customer_name=customer_name,
        customer_phone=customer_phone,
        special_instructions=special_instructions,
        status="pending",
        payment_status="unpaid",
    )

    # Create order items
    for cart_item in cart_items:

        OrderItem.objects.create(
            order=order,
            food=cart_item.food,
            quantity=cart_item.quantity,
            price=cart_item.food.price,
            special_instructions=cart_item.special_instructions,
        )

    # Remove items from cart
    cart_items.delete()

    # Show success page
    return render(
        request,
        "order_success.html",
        {
            "order": order
        }
    )


def home(request):

    categories = Category.objects.all()

    foods = Food.objects.filter(
        is_available=True
    ).select_related("category")

    tables = RestaurantTable.objects.filter(
        is_available=True
    )

    selected_category = request.GET.get("category")

    if selected_category:
        foods = foods.filter(
            category_id=selected_category
        )

    if not request.session.session_key:
        request.session.create()

    session_id = request.session.session_key

    cart_count = Cart.objects.filter(
        session_id=session_id
    ).count()

    return render(request, "home.html", {
        "categories": categories,
        "foods": foods,
        "tables": tables,
        "cart_count": cart_count,
        "selected_category": (
            int(selected_category)
            if selected_category
            else None
        ),
    })


def add_to_cart(request, food_id):

    food = get_object_or_404(
        Food,
        id=food_id,
        is_available=True
    )

    if not request.session.session_key:
        request.session.create()

    session_id = request.session.session_key

    cart_item, created = Cart.objects.get_or_create(
        session_id=session_id,
        food=food,
        defaults={
            "quantity": 1
        }
    )

    if not created:
        cart_item.quantity += 1
        cart_item.save()

    return redirect("home")


def cart(request):

    if not request.session.session_key:
        request.session.create()

    session_id = request.session.session_key

    cart_items = Cart.objects.filter(
        session_id=session_id
    ).select_related(
        "food",
        "table"
    )

    total = sum(
        item.subtotal
        for item in cart_items
    )

    return render(request, "cart.html", {
        "cart_items": cart_items,
        "total": total,
    })

def checkout(request):

    # Create session if it doesn't exist
    if not request.session.session_key:
        request.session.create()

    session_id = request.session.session_key

    # Get current user's cart
    cart_items = Cart.objects.filter(
        session_id=session_id
    ).select_related("food", "table")

    # Don't allow checkout with an empty cart
    if not cart_items.exists():
        return redirect("cart")

    # Get available restaurant tables
    tables = RestaurantTable.objects.filter(
        is_available=True
    )

    # Calculate total
    total = sum(
        item.subtotal
        for item in cart_items
    )

    return render(
        request,
        "checkout.html",
        {
            "cart_items": cart_items,
            "tables": tables,
            "total": total,
        }
    )
    
def manager_food_create(request):
    return render(request, "manager/food_create.html")

def manager_category_list(request):
    return render(request, "manager/category_list.html")


def manager_order_list(request):
    return render(request, "manager/order_list.html")

    
@login_required
def kitchen_dashboard(request):
    # Only allow chefs to access this page
    if not request.user.groups.filter(name="Chef").exists():
        return redirect("home")

    return render(request, "kitchen/dashboard.html")