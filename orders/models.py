from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

from products.models import Product


class Order(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending Payment"),
        ("paid", "Paid"),
        ("expired", "Expired"),
        ("cancelled", "Cancelled"),
    ]

    # NEW → Link order to logged-in user
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="orders"
    )

    # Customer info
    full_name = models.CharField(max_length=255)
    email = models.EmailField()
    note = models.TextField(blank=True, null=True)

    # Summary
    total = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")

    # BTCPay fields
    btcpay_invoice_id = models.CharField(max_length=200, blank=True, null=True)
    btcpay_status = models.CharField(max_length=50, blank=True, null=True)

    paid = models.BooleanField(default=False)

    # Timings
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Order {self.id} - {self.status}"


class OrderItem(models.Model):
    order = models.ForeignKey(
        Order,
        related_name="items",
        on_delete=models.CASCADE
    )
    product = models.ForeignKey(
        Product,
        related_name="order_items",
        on_delete=models.SET_NULL,
        null=True
    )
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.quantity} × {self.product}"


