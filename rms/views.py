from rest_framework.decorators import api_view
from django.views.decorators.csrf import ensure_csrf_cookie
from django.shortcuts import (render,get_object_or_404)
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from rest_framework import status
from rest_framework.generics import (ListCreateAPIView,RetrieveUpdateDestroyAPIView,)
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import (Category,Food,RestaurantTable,Order,Payment,OrderItem)
from .serializers import (CategorySerializer,FoodSerializer,RestaurantTableSerializer,OrderSerializer,PaymentSerializer,OrderStatusUpdateSerializer,)
from .models import Cart
from .serializers import CartSerializer
from django.db import transaction
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token
from django.shortcuts import render


# ==========================================
# STAFF LOGIN
# ==========================================

def home(request):
    foods = Food.objects.filter(is_available=True)
    categories = Category.objects.all()

    context = {
        "foods": foods,
        "categories": categories,
    }

    return render(request, "home.html", context)

@api_view(["POST"])
def staff_login(request):

    username = request.data.get("username")
    password = request.data.get("password")

    if not username or not password:
        return Response(
            {
                "error": "Username and password are required."
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    user = authenticate(
        username=username,
        password=password
    )

    if user is None:
        return Response(
            {
                "error": "Invalid username or password."
            },
            status=status.HTTP_401_UNAUTHORIZED
        )

    if not hasattr(user, "staff_profile"):
        return Response(
            {
                "error": "This user is not a staff member."
            },
            status=status.HTTP_403_FORBIDDEN
        )

    token, created = Token.objects.get_or_create(
        user=user
    )

    return Response(
        {
            "message": "Login successful.",
            "token": token.key,
            "user_id": user.id,
            "username": user.username,
            "role": user.staff_profile.role,
        },
        status=status.HTTP_200_OK
    )


# ==========================================
# CATEGORY
# ==========================================

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


# ==========================================
# CUSTOMER TABLE MENU
# ==========================================

def table_menu(request, table_number):

    table = get_object_or_404(
        RestaurantTable,
        table_number=table_number,
        is_available=True
    )

    foods = Food.objects.select_related(
        "category"
    ).order_by(
        "category__Category_name",
        "name"
    )

    return render(
        request,
        "home.html",
        {
            "table": table,
            "foods": foods,
        }
    )



# ==========================================
# FOOD
# ==========================================

class FoodListCreateAPIView(
    ListCreateAPIView
):

    queryset = Food.objects.select_related(
        "category"
    ).all()

    serializer_class = FoodSerializer


class FoodDetailAPIView(
    RetrieveUpdateDestroyAPIView
):

    queryset = Food.objects.select_related(
        "category"
    ).all()

    serializer_class = FoodSerializer


# ==========================================
# TABLE
# ==========================================

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

@api_view(["GET", "POST"])
def cart_list(request):

    if request.method == "GET":

        session_id = request.query_params.get("session_id")

        if not session_id:
            return Response(
                {"error": "session_id is required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        cart_items = Cart.objects.filter(
            session_id=session_id
        )

        serializer = CartSerializer(
            cart_items,
            many=True
        )

        return Response(serializer.data)

    if request.method == "POST":

        serializer = CartSerializer(
            data=request.data
        )

        if serializer.is_valid():

            serializer.save()

            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

@api_view(["PUT", "DELETE"])
def cart_detail(request, pk):

    try:
        cart_item = Cart.objects.get(pk=pk)

    except Cart.DoesNotExist:
        return Response(
            {"error": "Cart item not found."},
            status=status.HTTP_404_NOT_FOUND
        )

    if request.method == "PUT":

        serializer = CartSerializer(
            cart_item,
            data=request.data,
            partial=True
        )

        if serializer.is_valid():

            serializer.save()

            return Response(serializer.data)

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

    if request.method == "DELETE":

        cart_item.delete()

        return Response(
            {"message": "Cart item removed."},
            status=status.HTTP_204_NO_CONTENT
        )

# ==========================================
# ORDER
# ==========================================

class OrderListCreateAPIView(
    ListCreateAPIView
):

    queryset = Order.objects.prefetch_related(
        "items"
    ).select_related(
        "table"
    ).all()

    serializer_class = OrderSerializer


class OrderDetailAPIView(
    RetrieveUpdateDestroyAPIView
):

    queryset = Order.objects.prefetch_related(
        "items"
    ).select_related(
        "table"
    ).all()

    serializer_class = OrderSerializer


# ==========================================
# ORDER STATUS UPDATE
# ==========================================

@method_decorator(
    csrf_exempt,
    name="dispatch"
)
class OrderStatusUpdateAPIView(
    APIView
):

    # Allowed status changes
    allowed_transitions = {

        "pending": [
            "confirmed",
            "cancelled"
        ],

        "confirmed": [
            "preparing",
            "cancelled"
        ],

        "preparing": [
            "ready"
        ],

        "ready": [
            "served"
        ],

        "served": [
            "completed"
        ],

        "completed": [],

        "cancelled": [],
    }


    def patch(
        self,
        request,
        pk
    ):

        # Find order
        order = get_object_or_404(
            Order,
            pk=pk
        )


        # Validate request data
        serializer = OrderStatusUpdateSerializer(
            data=request.data
        )

        serializer.is_valid(
            raise_exception=True
        )


        # Current status
        current_status = order.status


        # Requested new status
        new_status = serializer.validated_data[
            "status"
        ]


        # Check allowed transition
        allowed_statuses = (
            self.allowed_transitions.get(
                current_status,
                []
            )
        )


        if new_status not in allowed_statuses:

            return Response(
                {
                    "success": False,

                    "error":
                        f"Cannot change status "
                        f"from '{current_status}' "
                        f"to '{new_status}'.",

                    "allowed_statuses":
                        allowed_statuses,
                },

                status=status.HTTP_400_BAD_REQUEST
            )


        # Save new status
        order.status = new_status

        order.save(
            update_fields=[
                "status",
                "updated_at"
            ]
        )


        # Return success response
        return Response(
            {
                "success": True,

                "message":
                    "Order status updated successfully.",

                "order_id":
                    order.id,

                "old_status":
                    current_status,

                "new_status":
                    order.status,
            },

            status=status.HTTP_200_OK
        )

@api_view(["POST"])
def checkout(request):

    session_id = request.data.get("session_id")

    if not session_id:
        return Response(
            {"error": "session_id is required."},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Get customer's cart
    cart_items = Cart.objects.filter(
        session_id=session_id
    ).select_related("food", "table")

    if not cart_items.exists():
        return Response(
            {"error": "Cart is empty."},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Customer information
    customer_name = request.data.get("customer_name")
    customer_phone = request.data.get("customer_phone")

    # Use table from cart
    table = cart_items.first().table

    if table is None:
        return Response(
            {"error": "Table is required."},
            status=status.HTTP_400_BAD_REQUEST
        )

    with transaction.atomic():

        # Create Order
        order = Order.objects.create(
            table=table,
            customer_name=customer_name,
            customer_phone=customer_phone,
            status="pending",
            payment_status="unpaid",
        )

        # Convert Cart → OrderItems
        for cart_item in cart_items:

            OrderItem.objects.create(
                order=order,
                food=cart_item.food,
                quantity=cart_item.quantity,
                price=cart_item.food.price,
                special_instructions=(
                    cart_item.special_instructions
                ),
            )

        # Clear cart after successful checkout
        cart_items.delete()

    serializer = OrderSerializer(order)

    return Response(
        serializer.data,
        status=status.HTTP_201_CREATED
    )
# ==========================================
# PAYMENT
# ==========================================

class PaymentListCreateAPIView(
    ListCreateAPIView
):

    queryset = Payment.objects.select_related(
        "order",
        "received_by"
    ).all()

    serializer_class = PaymentSerializer


class PaymentDetailAPIView(
    RetrieveUpdateDestroyAPIView
):

    queryset = Payment.objects.select_related(
        "order",
        "received_by"
    ).all()

    serializer_class = PaymentSerializer


# ==========================================
# CUSTOMER TABLE MENU
# ==========================================

def table_menu(
    request,
    table_number
):

    table = get_object_or_404(
        RestaurantTable,

        table_number=table_number,

        is_available=True
    )


    foods = Food.objects.select_related(
        "category"
    ).all()


    return render(
        request,

        "home.html",

        {
            "table": table,

            "foods": foods,
        }
    )


# ==========================================
# KITCHEN ORDERS API
# ==========================================

class KitchenOrderAPIView(
    APIView
):

    def get(
        self,
        request
    ):

        orders = Order.objects.filter(

            status__in=[
                "pending",
                "confirmed",
                "preparing",
            ]

        ).prefetch_related(

            "items__food"

        ).select_related(

            "table"

        ).order_by(

            "created_at"
        )


        serializer = OrderSerializer(
            orders,
            many=True
        )


        return Response(
            serializer.data
        )


# ==========================================
# KITCHEN DASHBOARD
# ==========================================
@ensure_csrf_cookie
def kitchen_dashboard(request):

    return render(
        request,
        "kitchen/dashboard.html"
    )

