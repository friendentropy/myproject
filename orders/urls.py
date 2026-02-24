from django.urls import path
from . import views
from .views import my_orders
app_name = "orders"

urlpatterns = [
    path("topup/", views.topup, name="topup"),
    # path("manual-payment/<int:order_id>/", views.manual_payment, name="manual_payment"),
    # path("topup/create-invoice/", views.create_topup_invoice, name="create_topup_invoice"),
    path("topup/manual/<int:order_id>/", views.manual_payment, name="manual_payment"),
    path("checkout/", views.checkout, name="checkout"),
    path("my-orders/", my_orders, name="my_orders"),

]
