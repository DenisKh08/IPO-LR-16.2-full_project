from django.shortcuts import render
from .models import Manufacturer, Category, Product, Cart

def catalog_view(request):
    manufacturers = Manufacturer.objects.all()
    categories = Category.objects.all()
    products = Product.objects.all()
    carts = Cart.objects.select_related('user').prefetch_related('items__product').all()

    context = {
        'manufacturers': manufacturers,
        'categories': categories,
        'products': products,
        'carts': carts,
    }
    return render(request, 'test.html', context)