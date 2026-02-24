from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from .models import Wallet, Transaction
from django.conf import settings

@login_required
def dashboard_home(request):
    # Get or create wallet safely
    wallet = Wallet.objects.filter(user=request.user).first()
    if not wallet:
        # create or set placeholder
        wallet = Wallet.objects.create(user=request.user, balance=0)  # only if Wallet model exists and safe
    recent_txs = Transaction.objects.filter(user=request.user).order_by('-created_at')[:5]
    return render(request, "dashboard/home.html", {
        "wallet": wallet,
        "recent_txs": recent_txs,
        "telegram_link": settings.TELEGRAM_LINK,
    })


def transactions_list(request):
    txs = Transaction.objects.filter(user=request.user).order_by("-created_at")
    return render(request, "dashboard/transactions.html", {"transactions": txs})


