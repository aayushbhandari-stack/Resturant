from decimal import Decimal

from django.shortcuts import (
    render,
    redirect,
    get_object_or_404,
)

from django.utils import timezone

from django.db import transaction

from django.db.models import (
    Sum,
    Count,
)

from django.contrib.auth import (
    authenticate,
    login,
    logout,
)

from django.contrib.auth.decorators import (
    login_required,
    user_passes_test,
)

from django.views.decorators.csrf import (
    ensure_csrf_cookie,
    csrf_exempt,
)

from django.utils.decorators import method_decorator

from rest_framework.decorators import api_view

from rest_framework import status

from rest_framework.generics import (
    ListCreateAPIView,
    RetrieveUpdateDestroyAPIView,
)

from rest_framework.response import Response

from rest_framework.views import APIView

from rest_framework.authtoken.models import Token


from .models import (
    Category,
    Food,
    RestaurantTable,
    Order,
    Payment,
    OrderItem,
    Cart,
    StaffProfile,
)

from .serializers import (
    CategorySerializer,
    FoodSerializer,
    RestaurantTableSerializer,
    OrderSerializer,
    PaymentSerializer,
    OrderStatusUpdateSerializer,
    CartSerializer,
)


# ============================================================
# ROLE CHECKING
# ============================================================

def is_manager(user):

    return (
        user.is_authenticated
        and user.groups.filter(
            name="Manager"
        ).exists()
    )


def is_reception(user):

    return (
        user.is_authenticated
        and user.groups.filter(
            name="Reception"
        ).exists()
    )


def is_waiter(user):

    return (
        user.is_authenticated
        and user.groups.filter(
            name="Waiter"
        ).exists()
    )


def is_chef(user):

    return (
        user.is_authenticated
        and user.groups.filter(
            name="Chef"
        ).exists()
    )


def is_staff_member(user):

    return (
        user.is_authenticated
        and user.groups.filter(
            name__in=[
                "Manager",
                "Reception",
                "Waiter",
                "Chef",
            ]
        ).exists()
    )


# ============================================================
# LOGIN
# ============================================================

@ensure_csrf_cookie
def login_view(request):

    if request.method == "POST":

        username = request.POST.get(
            "username",
            ""
        ).strip()

        password = request.POST.get(
            "password",
            ""
        )

        if not username or not password:

            return render(
                request,
                "login.html",
                {
                    "error":
                        "Username and password are required."
                },
            )

        user = authenticate(
            request=request,
            username=username,
            password=password,
        )

        if user is None:

            return render(
                request,
                "login.html",
                {
                    "error":
                        "Invalid username or password."
                },
            )

        allowed_roles = {
            "Manager",
            "Reception",
            "Waiter",
            "Chef",
        }

        roles = list(
            user.groups.values_list(
                "name",
                flat=True,
            )
        )

        user_roles = [
            role
            for role in roles
            if role in allowed_roles
        ]

        if not user_roles:

            return render(
                request,
                "login.html",
                {
                    "error":
                        f"User '{user.username}' "
                        "does not have a staff role."
                },
            )

        login(request, user)

        request.session["staff_username"] = (
            user.username
        )

        request.session["staff_roles"] = (
            user_roles
        )

        if "Manager" in user_roles:
            return redirect(
                "manager_dashboard"
            )

        if "Reception" in user_roles:
            return redirect(
                "reception_dashboard"
            )

        if "Waiter" in user_roles:
            return redirect(
                "waiter_dashboard"
            )

        if "Chef" in user_roles:
            return redirect(
                "kitchen_dashboard"
            )

        logout(request)

        return redirect("login")

    return render(
        request,
        "login.html",
    )


# ============================================================
# LOGOUT
# ============================================================

@login_required
def logout_view(request):

    logout(request)

    return redirect("login")


# ============================================================
# CUSTOMER HOME
# ============================================================

def home(request):

    categories = Category.objects.all()

    foods = (
        Food.objects
        .filter(is_available=True)
        .select_related("category")
    )

    tables = (
        RestaurantTable.objects
        .filter(is_available=True)
    )

    selected_category = request.GET.get(
        "category"
    )

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

    return render(
        request,
        "home.html",
        {
            "categories": categories,
            "foods": foods,
            "tables": tables,
            "cart_count": cart_count,
            "selected_category": (
                int(selected_category)
                if selected_category
                else None
            ),
        },
    )


# ============================================================
# QR TABLE MENU
# ============================================================

def qr_table_menu(
    request,
    qr_token,
):

    table = get_object_or_404(
        RestaurantTable,
        qr_token=qr_token,
        is_available=True,
    )

    if not request.session.session_key:
        request.session.create()

    request.session["qr_table_id"] = table.id

    request.session["qr_table_number"] = (
        table.table_number
    )

    request.session.modified = True

    foods = (
        Food.objects
        .select_related("category")
        .filter(is_available=True)
    )

    categories = Category.objects.all()

    cart_count = Cart.objects.filter(
        session_id=request.session.session_key
    ).count()

    return render(
        request,
        "home.html",
        {
            "table": table,
            "foods": foods,
            "categories": categories,
            "cart_count": cart_count,
        },
    )


# ============================================================
# TABLE MENU BY TABLE NUMBER
# ============================================================

def table_menu(
    request,
    table_number,
):

    table = get_object_or_404(
        RestaurantTable,
        table_number=table_number,
        is_available=True,
    )

    if not request.session.session_key:
        request.session.create()

    request.session["qr_table_id"] = table.id

    request.session["qr_table_number"] = (
        table.table_number
    )

    foods = (
        Food.objects
        .select_related("category")
        .filter(is_available=True)
    )

    categories = Category.objects.all()

    cart_count = Cart.objects.filter(
        session_id=request.session.session_key
    ).count()

    return render(
        request,
        "home.html",
        {
            "table": table,
            "foods": foods,
            "categories": categories,
            "cart_count": cart_count,
        },
    )


# ============================================================
# ADD TO CART
# ============================================================

def add_to_cart(
    request,
    food_id,
):

    food = get_object_or_404(
        Food,
        id=food_id,
        is_available=True,
    )

    if not request.session.session_key:
        request.session.create()

    session_id = request.session.session_key

    qr_table_id = request.session.get(
        "qr_table_id"
    )

    table = None

    if qr_table_id:

        table = (
            RestaurantTable.objects
            .filter(
                id=qr_table_id,
                is_available=True,
            )
            .first()
        )

    cart_item, created = (
        Cart.objects.get_or_create(
            session_id=session_id,
            food=food,
            defaults={
                "quantity": 1,
                "table": table,
            },
        )
    )

    if not created:

        cart_item.quantity += 1

        if table:
            cart_item.table = table

        cart_item.save()

    return redirect("home")


# ============================================================
# CART
# ============================================================

def cart(request):

    if not request.session.session_key:
        request.session.create()

    session_id = request.session.session_key

    cart_items = (
        Cart.objects
        .filter(session_id=session_id)
        .select_related(
            "food",
            "table",
        )
    )

    total = sum(
        item.subtotal
        for item in cart_items
    )

    return render(
        request,
        "cart.html",
        {
            "cart_items": cart_items,
            "total": total,
        },
    )


# ============================================================
# CHECKOUT
# ============================================================

def checkout(request):

    if not request.session.session_key:
        request.session.create()

    session_id = request.session.session_key

    cart_items = (
        Cart.objects
        .filter(session_id=session_id)
        .select_related(
            "food",
            "table",
        )
    )

    if not cart_items.exists():
        return redirect("cart")

    total = sum(
        item.subtotal
        for item in cart_items
    )

    qr_table_id = request.session.get(
        "qr_table_id"
    )

    table = None

    if qr_table_id:

        table = (
            RestaurantTable.objects
            .filter(
                id=qr_table_id,
                is_available=True,
            )
            .first()
        )

    return render(
        request,
        "checkout.html",
        {
            "cart_items": cart_items,
            "table": table,
            "total": total,
        },
    )


# ============================================================
# PLACE ORDER
# ============================================================

def place_order(request):

    if request.method != "POST":
        return redirect("checkout")

    if not request.session.session_key:
        request.session.create()

    session_id = request.session.session_key

    cart_items = (
        Cart.objects
        .filter(session_id=session_id)
        .select_related("food")
    )

    if not cart_items.exists():
        return redirect("cart")

    customer_name = request.POST.get(
        "customer_name",
        "",
    ).strip()

    customer_phone = request.POST.get(
        "customer_phone",
        "",
    ).strip()

    special_instructions = request.POST.get(
        "special_instructions",
        "",
    ).strip()

    qr_table_id = request.session.get(
        "qr_table_id"
    )

    if not qr_table_id:

        total = sum(
            item.subtotal
            for item in cart_items
        )

        return render(
            request,
            "checkout.html",
            {
                "cart_items": cart_items,
                "total": total,
                "error":
                    "Table not detected. "
                    "Please scan the table QR code again.",
            },
        )

    table = get_object_or_404(
        RestaurantTable,
        id=qr_table_id,
        is_available=True,
    )

    with transaction.atomic():

        order = Order.objects.create(
            table=table,
            customer_name=customer_name,
            customer_phone=customer_phone,
            special_instructions=(
                special_instructions
            ),
            status="pending",
            payment_status="unpaid",
        )

        for cart_item in cart_items:

            OrderItem.objects.create(
                order=order,
                food=cart_item.food,
                quantity=cart_item.quantity,
                price=cart_item.food.price,
                special_instructions=(
                    cart_item.special_instructions
                    or ""
                ),
            )

        cart_items.delete()

    request.session.pop(
        "qr_table_id",
        None,
    )

    request.session.pop(
        "qr_table_number",
        None,
    )

    request.session.modified = True

    return render(
        request,
        "order_success.html",
        {
            "order": order,
        },
    )


# ============================================================
# MANAGER DASHBOARD
# ============================================================

@login_required
@user_passes_test(is_manager)
def manager_dashboard(request):

    orders = (
        Order.objects
        .prefetch_related(
            "items__food"
        )
        .select_related("table")
        .order_by("-created_at")
    )

    staff_members = (
        StaffProfile.objects
        .select_related("user")
        .order_by("user__username")
    )

    return render(
        request,
        "manager/dashboard.html",
        {
            "orders": orders,

            "total_orders":
                orders.count(),

            "pending_orders":
                orders.filter(
                    status="pending"
                ).count(),

            "confirmed_orders":
                orders.filter(
                    status="confirmed"
                ).count(),

            "preparing_orders":
                orders.filter(
                    status="preparing"
                ).count(),

            "ready_orders":
                orders.filter(
                    status="ready"
                ).count(),

            "completed_orders":
                orders.filter(
                    status="completed"
                ).count(),

            "staff_members":
                staff_members,

            "total_staff":
                staff_members.count(),

            "staff_username":
                request.user.username,

            "staff_roles": list(
                request.user.groups.values_list(
                    "name",
                    flat=True,
                )
            ),
        },
    )


# ============================================================
# STAFF LIST
# ============================================================

@login_required
@user_passes_test(is_manager)
def staff_list(request):

    staff_members = (
        StaffProfile.objects
        .select_related("user")
        .order_by("user__username")
    )

    return render(
        request,
        "manager/staff_list.html",
        {
            "staff_members": staff_members,

            "staff_username":
                request.user.username,

            "staff_roles": list(
                request.user.groups.values_list(
                    "name",
                    flat=True,
                )
            ),
        },
    )


# ============================================================
# MANAGER FOOD LIST
# ============================================================

@login_required
@user_passes_test(is_manager)
def manager_food_list(request):

    foods = (
        Food.objects
        .select_related("category")
        .order_by("name")
    )

    return render(
        request,
        "manager/food_list.html",
        {
            "foods": foods,

            "staff_username":
                request.user.username,

            "staff_roles": list(
                request.user.groups.values_list(
                    "name",
                    flat=True,
                )
            ),
        },
    )


# ============================================================
# MANAGER FOOD CREATE
# ============================================================

@login_required
@user_passes_test(is_manager)
def manager_food_create(request):

    categories = Category.objects.all()

    if request.method == "POST":

        name = request.POST.get(
            "name",
            "",
        ).strip()

        price = request.POST.get(
            "price",
            "",
        )

        category_id = request.POST.get(
            "category"
        )

        is_available = (
            request.POST.get(
                "is_available"
            )
            == "on"
        )

        if (
            not name
            or not price
            or not category_id
        ):

            return render(
                request,
                "manager/food_create.html",
                {
                    "categories": categories,
                    "error":
                        "Name, price and category "
                        "are required.",
                },
            )

        category_obj = get_object_or_404(
            Category,
            id=category_id,
        )

        Food.objects.create(
            name=name,
            price=price,
            category=category_obj,
            is_available=is_available,
        )

        return redirect(
            "manager_food_list"
        )

    return render(
        request,
        "manager/food_create.html",
        {
            "categories": categories,
        },
    )


# ============================================================
# MANAGER FOOD EDIT
# ============================================================

@login_required
@user_passes_test(is_manager)
def manager_food_edit(
    request,
    food_id,
):

    food = get_object_or_404(
        Food,
        id=food_id,
    )

    categories = Category.objects.all()

    if request.method == "POST":

        name = request.POST.get(
            "name",
            "",
        ).strip()

        price = request.POST.get(
            "price",
            "",
        )

        category_id = request.POST.get(
            "category"
        )

        if (
            not name
            or not price
            or not category_id
        ):

            return render(
                request,
                "manager/food_edit.html",
                {
                    "food": food,
                    "categories": categories,
                    "error":
                        "Name, price and category "
                        "are required.",
                },
            )

        category_obj = get_object_or_404(
            Category,
            id=category_id,
        )

        food.name = name
        food.price = price
        food.category = category_obj

        food.is_available = (
            request.POST.get(
                "is_available"
            )
            == "on"
        )

        food.save()

        return redirect(
            "manager_food_list"
        )

    return render(
        request,
        "manager/food_edit.html",
        {
            "food": food,
            "categories": categories,
        },
    )


# ============================================================
# MANAGER FOOD DELETE
# ============================================================

@login_required
@user_passes_test(is_manager)
def manager_food_delete(
    request,
    food_id,
):

    food = get_object_or_404(
        Food,
        id=food_id,
    )

    if request.method == "POST":
        food.delete()

    return redirect(
        "manager_food_list"
    )


# ============================================================
# CATEGORY LIST
# ============================================================

@login_required
@user_passes_test(is_manager)
def manager_category_list(request):

    categories = (
        Category.objects
        .order_by("category_name")
    )

    return render(
        request,
        "manager/category_list.html",
        {
            "categories": categories,

            "staff_username":
                request.user.username,

            "staff_roles": list(
                request.user.groups.values_list(
                    "name",
                    flat=True,
                )
            ),
        },
    )


# ============================================================
# CATEGORY CREATE
# ============================================================

@login_required
@user_passes_test(is_manager)
def manager_category_create(request):

    if request.method == "POST":

        name = request.POST.get(
            "name",
            "",
        ).strip()

        if not name:

            return render(
                request,
                "manager/category_create.html",
                {
                    "error":
                        "Category name is required."
                },
            )

        Category.objects.create(
            category_name=name
        )

        return redirect(
            "manager_category_list"
        )

    return render(
        request,
        "manager/category_create.html"
    )


# ============================================================
# CATEGORY EDIT
# ============================================================

@login_required
@user_passes_test(is_manager)
def manager_category_edit(
    request,
    category_id,
):

    category_obj = get_object_or_404(
        Category,
        id=category_id,
    )

    if request.method == "POST":

        name = request.POST.get(
            "name",
            "",
        ).strip()

        if not name:

            return render(
                request,
                "manager/category_edit.html",
                {
                    "category": category_obj,
                    "error":
                        "Category name is required."
                },
            )

        category_obj.category_name = name

        category_obj.save()

        return redirect(
            "manager_category_list"
        )

    return render(
        request,
        "manager/category_edit.html",
        {
            "category": category_obj,
        },
    )


# ============================================================
# CATEGORY DELETE
# ============================================================

@login_required
@user_passes_test(is_manager)
def manager_category_delete(
    request,
    category_id,
):

    category_obj = get_object_or_404(
        Category,
        id=category_id,
    )

    if request.method == "POST":
        category_obj.delete()

    return redirect(
        "manager_category_list"
    )


# ============================================================
# MANAGER ORDER LIST
# ============================================================

@login_required
@user_passes_test(is_manager)
def manager_order_list(request):

    orders = (
        Order.objects
        .prefetch_related(
            "items__food"
        )
        .select_related("table")
        .order_by("-created_at")
    )

    return render(
        request,
        "manager/order_list.html",
        {
            "orders": orders,

            "staff_username":
                request.user.username,

            "staff_roles": list(
                request.user.groups.values_list(
                    "name",
                    flat=True,
                )
            ),
        },
    )


# ============================================================
# MANAGER ORDER STATUS
# ============================================================

@login_required
@user_passes_test(is_manager)
def manager_order_status(
    request,
    order_id,
):

    order = get_object_or_404(
        Order,
        id=order_id,
    )

    if request.method == "POST":

        new_status = request.POST.get(
            "status"
        )

        allowed_statuses = {
            "pending",
            "confirmed",
            "preparing",
            "ready",
            "served",
            "completed",
            "cancelled",
        }

        if new_status in allowed_statuses:

            order.status = new_status

            order.save(
                update_fields=[
                    "status",
                    "updated_at",
                ]
            )

    return redirect(
        "manager_order_list"
    )


# ============================================================
# MANAGER TABLE LIST
# ============================================================

@login_required
@user_passes_test(is_manager)
def manager_table_list(request):

    tables = (
        RestaurantTable.objects
        .order_by("table_number")
    )

    return render(
        request,
        "manager/table_list.html",
        {
            "tables": tables,

            "staff_username":
                request.user.username,

            "staff_roles": list(
                request.user.groups.values_list(
                    "name",
                    flat=True,
                )
            ),
        },
    )


# ============================================================
# MANAGER TABLE CREATE
# ============================================================

@login_required
@user_passes_test(is_manager)
def manager_table_create(request):

    if request.method == "POST":

        table_number = request.POST.get(
            "table_number",
            "",
        ).strip()

        is_available = (
            request.POST.get(
                "is_available"
            )
            == "on"
        )

        if not table_number:

            return render(
                request,
                "manager/table_create.html",
                {
                    "error":
                        "Table number is required."
                },
            )

        if RestaurantTable.objects.filter(
            table_number=table_number
        ).exists():

            return render(
                request,
                "manager/table_create.html",
                {
                    "error":
                        "This table number already exists."
                },
            )

        RestaurantTable.objects.create(
            table_number=table_number,
            is_available=is_available,
        )

        return redirect(
            "manager_table_list"
        )

    return render(
        request,
        "manager/table_create.html"
    )


# ============================================================
# MANAGER TABLE EDIT
# ============================================================

@login_required
@user_passes_test(is_manager)
def manager_table_edit(
    request,
    table_id,
):

    table = get_object_or_404(
        RestaurantTable,
        id=table_id,
    )

    if request.method == "POST":

        table_number = request.POST.get(
            "table_number",
            "",
        ).strip()

        if not table_number:

            return render(
                request,
                "manager/table_edit.html",
                {
                    "table": table,
                    "error":
                        "Table number is required."
                },
            )

        if RestaurantTable.objects.filter(
            table_number=table_number
        ).exclude(
            id=table.id
        ).exists():

            return render(
                request,
                "manager/table_edit.html",
                {
                    "table": table,
                    "error":
                        "This table number already exists."
                },
            )

        table.table_number = table_number

        table.is_available = (
            request.POST.get(
                "is_available"
            )
            == "on"
        )

        table.save()

        return redirect(
            "manager_table_list"
        )

    return render(
        request,
        "manager/table_edit.html",
        {
            "table": table,
        },
    )


# ============================================================
# MANAGER TABLE DELETE
# ============================================================

@login_required
@user_passes_test(is_manager)
def manager_table_delete(
    request,
    table_id,
):

    table = get_object_or_404(
        RestaurantTable,
        id=table_id,
    )

    if request.method == "POST":
        table.delete()

    return redirect(
        "manager_table_list"
    )


# ============================================================
# MANAGER TABLE QR
# ============================================================

@login_required
@user_passes_test(is_manager)
def manager_table_qr(
    request,
    table_id,
):

    table = get_object_or_404(
        RestaurantTable,
        id=table_id,
    )

    customer_url = request.build_absolute_uri(
        f"/order/table/{table.qr_token}/"
    )

    return render(
        request,
        "manager/table_qr.html",
        {
            "table": table,
            "customer_url": customer_url,
        },
    )


# ============================================================
# RECEPTION DASHBOARD
# ============================================================

@login_required
@user_passes_test(is_reception)
def reception_dashboard(request):

    orders = (
        Order.objects
        .prefetch_related(
            "items__food"
        )
        .select_related("table")
        .order_by("-created_at")
    )

    return render(
        request,
        "reception/dashboard.html",
        {
            "orders": orders,

            "staff_username":
                request.user.username,

            "staff_roles": list(
                request.user.groups.values_list(
                    "name",
                    flat=True,
                )
            ),
        },
    )


# ============================================================
# RECEPTION CUSTOMER LIST
# ============================================================

@login_required
@user_passes_test(is_reception)
def reception_customer_list(request):

    customers = (
        Order.objects
        .exclude(customer_name="")
        .values(
            "customer_name",
            "customer_phone",
        )
        .annotate(
            order_count=Count("id")
        )
        .order_by("customer_name")
    )

    return render(
        request,
        "reception/customer_list.html",
        {
            "customers": customers,
        },
    )


# ============================================================
# RECEPTION ORDER LIST
# ============================================================

@login_required
@user_passes_test(is_reception)
def reception_order_list(request):

    orders = (
        Order.objects
        .prefetch_related(
            "items__food"
        )
        .select_related("table")
        .order_by("-created_at")
    )

    return render(
        request,
        "reception/order_list.html",
        {
            "orders": orders,
        },
    )


# ============================================================
# RECEPTION PAYMENT LIST
# ============================================================

@login_required
@user_passes_test(is_reception)
def reception_payment_list(request):

    payments = (
        Payment.objects
        .select_related(
            "order",
            "received_by",
        )
        .order_by("-paid_at")
    )

    return render(
        request,
        "reception/payment_list.html",
        {
            "payments": payments,
        },
    )


# ============================================================
# RECEPTION TABLE LIST
# ============================================================

@login_required
@user_passes_test(is_reception)
def reception_table_list(request):

    tables = (
        RestaurantTable.objects
        .order_by("table_number")
    )

    return render(
        request,
        "reception/table_list.html",
        {
            "tables": tables,
        },
    )


# ============================================================
# WAITER DASHBOARD
# ============================================================

@login_required
@user_passes_test(is_waiter)
def waiter_dashboard(request):

    orders = (
        Order.objects
        .filter(
            status__in=[
                "confirmed",
                "preparing",
                "ready",
            ]
        )
        .prefetch_related(
            "items__food"
        )
        .select_related("table")
        .order_by("created_at")
    )

    return render(
        request,
        "waiter/dashboard.html",
        {
            "orders": orders,

            "staff_username":
                request.user.username,

            "staff_roles": list(
                request.user.groups.values_list(
                    "name",
                    flat=True,
                )
            ),
        },
    )


# ============================================================
# KITCHEN DASHBOARD
# ============================================================

@login_required
@user_passes_test(is_chef)
def kitchen_dashboard(request):

    orders = (
        Order.objects
        .filter(
            status__in=[
                "confirmed",
                "preparing",
                "ready",
            ]
        )
        .prefetch_related(
            "items__food"
        )
        .select_related("table")
        .order_by("created_at")
    )

    return render(
        request,
        "kitchen/dashboard.html",
        {
            "orders": orders,

            "confirmed_orders":
                orders.filter(
                    status="confirmed"
                ).count(),

            "preparing_orders":
                orders.filter(
                    status="preparing"
                ).count(),

            "ready_orders":
                orders.filter(
                    status="ready"
                ).count(),

            "completed_orders":
                Order.objects.filter(
                    status="completed"
                ).count(),

            "staff_username":
                request.user.username,

            "staff_roles": list(
                request.user.groups.values_list(
                    "name",
                    flat=True,
                )
            ),
        },
    )


# ============================================================
# CHEF ORDER STATUS UPDATE
# ============================================================

@login_required
@user_passes_test(is_chef)
def chef_order_status(
    request,
    order_id,
):

    order = get_object_or_404(
        Order,
        id=order_id,
    )

    if request.method == "POST":

        new_status = request.POST.get(
            "status"
        )

        allowed_transitions = {

            "confirmed": [
                "preparing",
            ],

            "preparing": [
                "ready",
            ],

            "ready": [
                "completed",
            ],

            "completed": [],

            "cancelled": [],
        }

        current_status = order.status

        allowed_statuses = (
            allowed_transitions.get(
                current_status,
                [],
            )
        )

        if new_status in allowed_statuses:

            order.status = new_status

            order.save(
                update_fields=[
                    "status",
                    "updated_at",
                ]
            )

    return redirect(
        "kitchen_dashboard"
    )


# ============================================================
# PAYMENT API
# ============================================================

class PaymentListCreateAPIView(
    ListCreateAPIView
):

    queryset = (
        Payment.objects
        .select_related(
            "order",
            "received_by",
        )
        .all()
    )

    serializer_class = PaymentSerializer


class PaymentDetailAPIView(
    RetrieveUpdateDestroyAPIView
):

    queryset = (
        Payment.objects
        .select_related(
            "order",
            "received_by",
        )
        .all()
    )

    serializer_class = PaymentSerializer


# ============================================================
# FOOD API
# ============================================================

class FoodListCreateAPIView(
    ListCreateAPIView
):

    queryset = (
        Food.objects
        .select_related("category")
        .all()
    )

    serializer_class = FoodSerializer


class FoodDetailAPIView(
    RetrieveUpdateDestroyAPIView
):

    queryset = (
        Food.objects
        .select_related("category")
        .all()
    )

    serializer_class = FoodSerializer


# ============================================================
# CATEGORY API
# ============================================================

class CategoryListCreateAPIView(
    ListCreateAPIView
):

    queryset = Category.objects.all()

    serializer_class = CategorySerializer


class CategoryDetailAPIView(
    RetrieveUpdateDestroyAPIView
):

    queryset = Category.objects.all()

    serializer_class = CategorySerializer


# ============================================================
# TABLE API
# ============================================================

class TableListCreateAPIView(
    ListCreateAPIView
):

    queryset = RestaurantTable.objects.all()

    serializer_class = RestaurantTableSerializer


class TableDetailAPIView(
    RetrieveUpdateDestroyAPIView
):

    queryset = RestaurantTable.objects.all()

    serializer_class = RestaurantTableSerializer


# ============================================================
# CART API
# ============================================================

@api_view(["GET", "POST"])
def cart_list(request):

    if request.method == "GET":

        session_id = request.query_params.get(
            "session_id"
        )

        if not session_id:

            return Response(
                {
                    "error":
                        "session_id is required."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        cart_items = (
            Cart.objects
            .filter(
                session_id=session_id
            )
            .select_related("food")
        )

        serializer = CartSerializer(
            cart_items,
            many=True,
        )

        return Response(
            serializer.data
        )

    serializer = CartSerializer(
        data=request.data
    )

    if serializer.is_valid():

        serializer.save()

        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED,
        )

    return Response(
        serializer.errors,
        status=status.HTTP_400_BAD_REQUEST,
    )


@api_view(["PUT", "DELETE"])
def cart_detail(
    request,
    pk,
):

    cart_item = get_object_or_404(
        Cart,
        pk=pk,
    )

    if request.method == "PUT":

        serializer = CartSerializer(
            cart_item,
            data=request.data,
            partial=True,
        )

        if serializer.is_valid():

            serializer.save()

            return Response(
                serializer.data
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST,
        )

    cart_item.delete()

    return Response(
        status=status.HTTP_204_NO_CONTENT
    )


# ============================================================
# ORDER API
# ============================================================

class OrderListCreateAPIView(
    ListCreateAPIView
):

    queryset = (
        Order.objects
        .prefetch_related(
            "items__food"
        )
        .select_related("table")
        .all()
    )

    serializer_class = OrderSerializer


class OrderDetailAPIView(
    RetrieveUpdateDestroyAPIView
):

    queryset = (
        Order.objects
        .prefetch_related(
            "items__food"
        )
        .select_related("table")
        .all()
    )

    serializer_class = OrderSerializer


# ============================================================
# ORDER STATUS API
# ============================================================

@method_decorator(
    csrf_exempt,
    name="dispatch",
)
class OrderStatusUpdateAPIView(
    APIView
):

    allowed_transitions = {

        "pending": [
            "confirmed",
            "cancelled",
        ],

        "confirmed": [
            "preparing",
            "cancelled",
        ],

        "preparing": [
            "ready",
        ],

        "ready": [
            "served",
            "completed",
        ],

        "served": [
            "completed",
        ],

        "completed": [],

        "cancelled": [],
    }

    def patch(
        self,
        request,
        pk,
    ):

        order = get_object_or_404(
            Order,
            pk=pk,
        )

        serializer = OrderStatusUpdateSerializer(
            data=request.data
        )

        serializer.is_valid(
            raise_exception=True
        )

        current_status = order.status

        new_status = (
            serializer.validated_data["status"]
        )

        allowed_statuses = (
            self.allowed_transitions.get(
                current_status,
                [],
            )
        )

        if new_status not in allowed_statuses:

            return Response(
                {
                    "success": False,

                    "error":
                        (
                            f"Cannot change status "
                            f"from '{current_status}' "
                            f"to '{new_status}'."
                        ),

                    "allowed_statuses":
                        allowed_statuses,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        order.status = new_status

        order.save(
            update_fields=[
                "status",
                "updated_at",
            ]
        )

        return Response(
            {
                "success": True,
                "order_id": order.id,
                "old_status": current_status,
                "new_status": order.status,
            },
            status=status.HTTP_200_OK,
        )


# ============================================================
# STAFF LOGIN API
# ============================================================

@api_view(["POST"])
def staff_login(request):

    username = request.data.get(
        "username"
    )

    password = request.data.get(
        "password"
    )

    if not username or not password:

        return Response(
            {
                "error":
                    "Username and password are required."
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    user = authenticate(
        request=request,
        username=username,
        password=password,
    )

    if user is None:

        return Response(
            {
                "error":
                    "Invalid username or password."
            },
            status=status.HTTP_401_UNAUTHORIZED,
        )

    roles = list(
        user.groups.values_list(
            "name",
            flat=True,
        )
    )

    if not user.groups.filter(
        name__in=[
            "Manager",
            "Reception",
            "Waiter",
            "Chef",
        ]
    ).exists():

        return Response(
            {
                "error":
                    "This user is not a staff member."
            },
            status=status.HTTP_403_FORBIDDEN,
        )

    token, created = (
        Token.objects.get_or_create(
            user=user
        )
    )

    return Response(
        {
            "message":
                "Login successful.",

            "token":
                token.key,

            "user_id":
                user.id,

            "username":
                user.username,

            "roles":
                roles,
        },
        status=status.HTTP_200_OK,
    )


# ============================================================
# KITCHEN API
# ============================================================

class KitchenOrderAPIView(
    APIView
):

    def get(self, request):

        if not request.user.is_authenticated:

            return Response(
                {
                    "error":
                        "Authentication required."
                },
                status=status.HTTP_401_UNAUTHORIZED,
            )

        if not is_chef(request.user):

            return Response(
                {
                    "error":
                        "Chef access required."
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        orders = (
            Order.objects
            .filter(
                status__in=[
                    "confirmed",
                    "preparing",
                    "ready",
                ]
            )
            .prefetch_related(
                "items__food"
            )
            .select_related("table")
            .order_by("created_at")
        )

        serializer = OrderSerializer(
            orders,
            many=True,
        )

        return Response(
            serializer.data
        )


# ============================================================
# STAFF ORDERS API
# ============================================================

class StaffOrderAPIView(
    APIView
):

    def get(self, request):

        if not request.user.is_authenticated:

            return Response(
                {
                    "error":
                        "Authentication required."
                },
                status=status.HTTP_401_UNAUTHORIZED,
            )

        if not is_staff_member(
            request.user
        ):

            return Response(
                {
                    "error":
                        "Staff access required."
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        orders = (
            Order.objects
            .prefetch_related(
                "items__food"
            )
            .select_related("table")
            .order_by("-created_at")
        )

        serializer = OrderSerializer(
            orders,
            many=True,
        )

        return Response(
            serializer.data
        )


# ============================================================
# RECEPTION DASHBOARD API
# ============================================================

@api_view(["GET"])
def reception_dashboard_api(request):

    if not request.user.is_authenticated:

        return Response(
            {
                "error":
                    "Authentication required."
            },
            status=status.HTTP_401_UNAUTHORIZED,
        )

    if not is_reception(
        request.user
    ):

        return Response(
            {
                "error":
                    "Reception access required."
            },
            status=status.HTTP_403_FORBIDDEN,
        )

    today = timezone.localdate()

    today_orders = Order.objects.filter(
        created_at__date=today
    )

    pending_orders = Order.objects.filter(
        status="pending"
    )

    available_tables = (
        RestaurantTable.objects
        .filter(is_available=True)
    )

    today_revenue = (
        Payment.objects
        .filter(
            paid_at__date=today
        )
        .aggregate(
            total=Sum("amount")
        )["total"]
        or Decimal("0.00")
    )

    recent_orders = (
        Order.objects
        .select_related("table")
        .prefetch_related(
            "items__food"
        )
        .order_by("-created_at")[:5]
    )

    recent_orders_data = []

    for order in recent_orders:

        recent_orders_data.append(
            {
                "id": order.id,

                "table_number": (
                    order.table.table_number
                    if order.table
                    else None
                ),

                "customer_name":
                    order.customer_name,

                "status":
                    order.status,

                "payment_status":
                    order.payment_status,

                "total_amount":
                    str(order.total_amount),

                "created_at":
                    order.created_at,
            }
        )

    tables = (
        RestaurantTable.objects
        .order_by("table_number")
    )

    tables_data = []

    for table in tables:

        tables_data.append(
            {
                "id": table.id,

                "table_number":
                    table.table_number,

                "is_available":
                    table.is_available,
            }
        )

    return Response(
        {
            "today_orders":
                today_orders.count(),

            "pending_orders":
                pending_orders.count(),

            "available_tables":
                available_tables.count(),

            "today_revenue":
                str(today_revenue),

            "recent_orders":
                recent_orders_data,

            "tables":
                tables_data,
        }
    )
