from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from .models import Product, Category, Manufacturer, Cart, CartItem

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

def product_list(request):
    products = Product.objects.all()
    categories = Category.objects.all()
    manufacturers = Manufacturer.objects.all()

    query = request.GET.get('q')
    cat_id = request.GET.get('category')
    man_id = request.GET.get('manufacturer')

    if query:
        products = products.filter(Q(name__icontains=query) | Q(description__icontains=query))
    if cat_id:
        products = products.filter(category_id=cat_id)
    if man_id:
        products = products.filter(manufacturer_id=man_id)

    return render(request, 'shop/product_list.html', {
        'products': products,
        'categories': categories,
        'manufacturers': manufacturers
    })

def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    return render(request, 'shop/product_detail.html', {'product': product})

@login_required
def cart_view(request):
    cart, created = Cart.objects.get_or_create(user=request.user)
    return render(request, 'shop/cart.html', {'cart': cart})

@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart, created = Cart.objects.get_or_create(user=request.user)
    
    cart_item, item_created = CartItem.objects.get_or_create(
        cart=cart, product=product, defaults={'quantity': 1}
    )
    
    if not item_created:
        if cart_item.quantity < product.stock:
            cart_item.quantity += 1
            cart_item.save()
        else:
            messages.error(request, "Недостаточно товара на складе.")
            
    return redirect('catalog:cart_view')

@login_required
def update_cart(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    new_quantity = int(request.POST.get('quantity', 1))
    
    if new_quantity <= cart_item.product.stock:
        cart_item.quantity = new_quantity
        cart_item.save()
    else:
        messages.error(request, f"Максимально доступно: {cart_item.product.stock}")
        
    return redirect('catalog:cart_view')

@login_required
def remove_from_cart(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    cart_item.delete()
    return redirect('catalog:cart_view')