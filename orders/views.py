from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponseBadRequest, HttpResponse, HttpRequest
from django.conf import settings
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt

import qrcode
import json
import hmac
import hashlib
import base64
import requests

from io import BytesIO
from .models import Order, OrderItem
from products.cart import Cart



# Load BTCPay settings from Django settings.py
BTCPAY_URL = getattr(settings, "BTCPAY_URL", "")
BTCPAY_STORE_ID = getattr(settings, "BTCPAY_STORE_ID", "")
BTCPAY_API_KEY = getattr(settings, "BTCPAY_API_KEY", "")
BTCPAY_WEBHOOK_SECRET = getattr(settings, "BTCPAY_WEBHOOK_SECRET", "")  # REQUIRED for signature verification


@login_required
def my_orders(request):
    orders = Order.objects.filter(user=request.user).order_by("-created")
    return render(request, "orders/my_orders.html", {"orders": orders})

@login_required
def topup(request):
    """
    TEMPORARY MANUAL TOP-UP (Month 1)
    Creates an Order, then redirects to manual payment page
    """

    if request.method == "POST":
        amount = request.POST.get("amount")

        if not amount:
            return render(request, "orders/topup.html", {
                "error": "Please enter an amount."
            })

        # 1️⃣ Create an order FIRST
        order = Order.objects.create(
            user=request.user,
            total=amount,
            full_name=request.user.username,
            email=request.user.email,
            note="Manual crypto top-up (temporary)",
        )

        # 2️⃣ Save amount (optional, but OK)
        request.session["manual_payment_amount"] = amount

        # 3️⃣ Redirect WITH order_id ✅
        return redirect("orders:manual_payment", order_id=order.id)

    return render(request, "orders/topup.html")



# @login_required
# def topup(request):
#     if request.method == "POST":
#         amount = request.POST.get("amount")
#
#         # Build the request to BTCPay Server
#         url = f"{settings.BTCPAY_URL}/api/v1/stores/{settings.BTCPAY_STORE_ID}/invoices"
#
#         headers = {
#             "Authorization": f"token {settings.BTCPAY_API_KEY}",
#             "Content-Type": "application/json"
#         }
#
#         data = {
#             "amount": amount,
#             "currency": "USD",     # or KES if you configured that
#             "metadata": {
#                 "orderId": f"TOPUP-{request.user.id}",
#                 "buyerName": request.user.username
#             }
#         }
#
#         response = requests.post(url, json=data, headers=headers)
#
#         if response.status_code == 200:
#             invoice = response.json()
#             return redirect(invoice["checkoutLink"])
#         else:
#             return render(request, "orders/topup.html", {
#                 "error": "Failed to create BTCPay invoice. Check settings or API key."
#             })
#
#     return render(request, "orders/topup.html")

# def create_topup_invoice(request: HttpRequest):
#     if request.method != "POST":
#         return HttpResponse("Invalid method", status=405)
#
#     # Get amount from POST form
#     amount = request.POST.get("amount")
#     if not amount:
#         return HttpResponse("Missing amount", status=400)
#
#     # Greenfield Invoices endpoint
#     url = f"{settings.BTCPAY_URL}/api/v1/stores/{settings.BTCPAY_STORE_ID}/invoices"
#
#     headers = {
#         "Content-Type": "application/json",
#         "Authorization": f"token {settings.BTCPAY_API_KEY}",
#     }
#
#     # Invoice payload
#     payload = {
#         "amount": amount,
#         "currency": "USD",
#         "metadata": {
#             "type": "wallet_topup",
#             "user_id": request.user.id,
#             "amount": amount,
#         }
#     }
#
#     # Send request
#     response = requests.post(url, json=payload, headers=headers)
#
#     # Parse BTCPay response JSON
#     try:
#         invoice = response.json()
#     except Exception:
#         return HttpResponse("BTCPay returned invalid JSON", status=500)
#
#     print("=== BTCPAY RESPONSE (GREENFIELD) ===")
#     print(invoice)
#
#     # If BTCPay returns an error
#     if "code" in invoice and invoice.get("code") != 0:
#         return HttpResponse(f"BTCPay Error: {invoice}", status=500)
#
#     # Extract checkoutLink
#     checkout_url = invoice.get("checkoutLink")
#     if not checkout_url:
#         return HttpResponse(f"BTCPay did NOT return checkoutLink: {invoice}", status=500)
#
#     # Redirect user to BTCPay invoice screen
#     return redirect(checkout_url)



# --------------------------------------------
# CHECKOUT VIEW — creates a local order + BTCPay invoice
# --------------------------------------------

def generate_qr(data):
    qr = qrcode.make(data)
    buffer = BytesIO()
    qr.save(buffer, format="PNG")
    return base64.b64encode(buffer.getvalue()).decode()


def manual_payment(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    amount = request.session.get("manual_payment_amount")

    if not amount:
        return redirect("orders:topup")

    btc_qr = generate_qr(settings.BTC_ADDRESS)
    ltc_qr = generate_qr(settings.LTC_ADDRESS)
    usdt_qr = generate_qr(settings.USDT_ADDRESS)
    eth_qr = generate_qr(settings.ETH_ADDRESS)

    return render(request, "orders/manual_payment.html", {
        "order": order,
        "amount": amount,
        "btc_address": settings.BTC_ADDRESS,
        "ltc_address": settings.LTC_ADDRESS,
        "usdt_address": settings.USDT_ADDRESS,
        "eth_address": settings.ETH_ADDRESS,
        "btc_qr": btc_qr,
        "ltc_qr": ltc_qr,
        "usdt_qr": usdt_qr,
        "eth_qr": eth_qr,
    })



@login_required
def checkout(request):
    cart = Cart(request)

    if request.method == "POST":
        full_name = request.POST.get("full_name", "").strip()
        email = request.POST.get("email", "").strip()
        note = request.POST.get("note", "").strip()

        if cart.get_total() <= 0:
            return HttpResponseBadRequest("Cart is empty")

        # 1️⃣ Create local order
        order = Order.objects.create(
            user=request.user,
            total=cart.get_total(),
            full_name=full_name,
            email=email,
            note=note,
        )

        # 2️⃣ Create order items
        for item in cart:
            OrderItem.objects.create(
                order=order,
                product=item["product"],
                price=item["price"],
                quantity=item["quantity"],
            )

        cart.clear()

        # 3️⃣ SWITCH PAYMENT MODE
        if settings.PAYMENT_MODE == "manual":
            return redirect("orders:manual_payment", order_id=order.id)

        # 4️⃣ BTCPAY FLOW (UNCHANGED)
        payload = {
            "amount": str(order.total),
            "currency": "USD",
            "checkout": {
                "speedPolicy": "HighSpeed",
                "redirectUrl": request.build_absolute_uri(
                    reverse("orders:thank_you", args=[order.id])
                ),
            },
            "metadata": {
                "order_id": order.id,
                "customer_name": full_name,
                "customer_email": email,
                "note": note,
            },
        }

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"token {BTCPAY_API_KEY}",
        }

        invoices_url = f"{BTCPAY_URL}/api/v1/stores/{BTCPAY_STORE_ID}/invoices"

        try:
            response = requests.post(
                invoices_url,
                headers=headers,
                json=payload,
                timeout=15,
            )
            response.raise_for_status()
        except requests.RequestException:
            order.delete()
            return render(
                request,
                "orders/checkout.html",
                {"cart": cart, "error": "Unable to create BTCPay invoice."},
            )

        invoice = response.json()
        order.btcpay_invoice_id = invoice.get("id")
        order.save()

        return redirect(invoice.get("checkoutLink"))

    # GET request
    return render(request, "orders/checkout.html", {"cart": cart})


# --------------------------------------------
# BTCPAY WEBHOOK — with HMAC signature verification
# --------------------------------------------
@csrf_exempt
def btcpay_webhook(request):
    if request.method != "POST":
        return HttpResponseBadRequest("Invalid method")

    # --- 1) PARSE BODY SAFELY ---
    try:
        raw_body = request.body
        print("RAW BODY:", raw_body)
        print("HEADERS:", request.headers)
        payload = json.loads(raw_body)
    except json.JSONDecodeError:
        return HttpResponseBadRequest("Invalid JSON")

    # --- 2) GET SIGNATURE HEADER ---
    signature = (
            request.headers.get("BTCPay-Signature")
            or request.headers.get("Btcpay-Sig")
    )
    if not signature:
        return HttpResponseBadRequest("Missing signature")

    try:
        algo, sig_hash = signature.split("=", 1)
    except ValueError:
        return HttpResponseBadRequest("Bad signature format")

    if algo != "sha256":
        return HttpResponseBadRequest("Unknown signature algorithm")

    # --- 3) VERIFY SIGNATURE ---
    mac = hmac.new(
        BTCPAY_WEBHOOK_SECRET.encode(),
        msg=raw_body,
        digestmod=hashlib.sha256,
    )
    expected = mac.hexdigest()

    if not hmac.compare_digest(expected, sig_hash):
        return HttpResponseBadRequest("Invalid signature")

    # --- 4) PROCESS REAL BTCPAY EVENTS ---
    event_type = payload.get("type")  # e.g. InvoiceCreated, InvoiceSettled
    invoice_id = payload.get("invoiceId")

    if not invoice_id:
        return HttpResponseBadRequest("Missing invoiceId")

    # Debug prints (optional)
    print("=== BTCPay Webhook Received ===")
    print("Event:", event_type)
    print("Invoice ID:", invoice_id)
    print("Payload:", payload)

    try:
        order = Order.objects.get(btcpay_invoice_id=invoice_id)
    except Order.DoesNotExist:
        return HttpResponseBadRequest("Order not found")

