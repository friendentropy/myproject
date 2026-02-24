from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.http import require_POST

from .models import Product, Category
from .cart import Cart

@login_required
def product_list(request, category_slug=None):
    products = Product.objects.filter(available=True).order_by("?")
    categories = Category.objects.all()
    category = None
    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        products = products.filter(category=category).order_by("?")
    return render(request, "products/product_list.html", {
        "products": products,
        "category": category,
        "categories": categories
    })


@login_required
def product_detail(request, slug):
    """
    Product detail view by slug.
    """
    product = get_object_or_404(Product, slug=slug, active=True)
    return render(request, "products/detail.html", {"product": product})

@login_required
@require_POST
def cart_add(request, product_id):
    """
    Add product to cart (POST).
    """
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id, active=True)
    quantity = int(request.POST.get("quantity", 1))
    override = bool(request.POST.get("override", False))
    cart.add(product=product, quantity=quantity, override_quantity=override)
    return redirect("products:product_list")

@login_required
def cart_detail(request):
    """
    Show cart contents.
    """
    cart = Cart(request)
    return render(request, "products/cart.html", {"cart": cart})

@login_required
@require_POST
def cart_remove(request, product_id):
    """
    Remove product from cart (POST).
    """
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    cart.remove(product)
    return redirect("products:cart_detail")

# def product_list_by_category(request, category_slug):
#     category = Category.objects.get(slug=category_slug)
#     products = Product.objects.filter(category=category)
#     return render(request, "products/product_list.html", {
#         "products": products,
#         "category": category
#     })

