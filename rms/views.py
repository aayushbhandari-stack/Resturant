from django.views.decorators.csrf import ensure_csrf_cookie
from django.shortcuts import (
    render,
    get_object_or_404
)

from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

from rest_framework import status
from rest_framework.generics import (
    ListCreateAPIView,
    RetrieveUpdateDestroyAPIView,
)
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import (
    Category,
    Food,
    RestaurantTable,
    Order,
    Payment,
)

from .serializers import (
    CategorySerializer,
    FoodSerializer,
    RestaurantTableSerializer,
    OrderSerializer,
    PaymentSerializer,
    OrderStatusUpdateSerializer,
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

