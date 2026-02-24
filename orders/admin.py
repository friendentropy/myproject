from django.contrib import admin
from .models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ("product", "price", "quantity", "subtotal")

    def subtotal(self, obj):
        return obj.price * obj.quantity

    subtotal.short_description = "Subtotal"


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "full_name", "email", "total", "paid", "created", "btcpay_invoice_id")
    list_filter = ("paid", "created")
    search_fields = ("full_name", "email", "btcpay_invoice_id")
    readonly_fields = (
        "created",
        "updated",
        "btcpay_invoice_id",
        "paid",
        "total",
    )
    inlines = [OrderItemInline]

    fieldsets = (
        ("Order Info", {
            "fields": ("full_name", "email", "note")
        }),
        ("Payment", {
            "fields": ("total", "paid", "btcpay_invoice_id")
        }),
        ("Timestamps", {
            "fields": ("created", "updated")
        }),
    )


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ("order", "product", "price", "quantity", "subtotal")

    def subtotal(self, obj):
        return obj.price * obj.quantity

    subtotal.short_description = "Subtotal"
