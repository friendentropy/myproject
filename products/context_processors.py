from .cart import Cart
from .models import Category

def categories_processor(request):
    return {
        "categories": Category.objects.all()
    }

def cart(request):
    return {'cart': Cart(request)}
