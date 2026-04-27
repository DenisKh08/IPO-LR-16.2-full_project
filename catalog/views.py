from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from .models import Product, Category, Manufacturer, Cart, CartItem
import openpyxl
from io import BytesIO
from django.core.mail import EmailMessage
from django.conf import settings
from rest_framework import viewsets, permissions
from .serializers import (
    ProductSerializer, CategorySerializer, ManufacturerSerializer,
    CartSerializer, CartItemSerializer
)
from django.core.paginator import Paginator

def main(request):
    popular_products = Product.objects.all().order_by('-id')[:6]
    categories = Category.objects.all()


    for product in popular_products:
        if not product.image:
            product.has_image = False
        else:
            product.has_image = True
    
    return render(request, 'main.html', {
        'popular_products': popular_products,
        'categories': categories,
    })

def shop(request):
    return render(request, "shop.html")

def about(request):
    return render(request, "about.html")

def catalog_view(request):
    products = Product.objects.all()
    categories = Category.objects.all()
    manufacturers = Manufacturer.objects.all()
    
    query = request.GET.get('q', '')
    cat_id = request.GET.get('category', '')
    man_id = request.GET.get('manufacturer', '')
    
    if query:
        products = products.filter(
            Q(name__icontains=query) | 
            Q(description__icontains=query)
        )
    if cat_id:
        products = products.filter(category_id=cat_id)
    if man_id:
        products = products.filter(manufacturer_id=man_id)
    
    paginator = Paginator(products, 9)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    context = {
        'products': page_obj,
        'categories': categories,
        'manufacturers': manufacturers,
        'current_category': cat_id,
        'current_manufacturer': man_id,
        'search_query': query,
    }
    return render(request, 'shop/catalog.html', context)

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

@login_required
def checkout(request):
    cart = get_object_or_404(Cart, user=request.user)
    
    if not cart.items.exists():
        messages.error(request, "Ваша корзина пуста")
        return redirect('catalog:cart_view')

    if request.method == 'POST':
        address = request.POST.get('address')
        
        #Генерация Excel-чека
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Чек"
        ws.append(["Товар", "Количество", "Цена", "Сумма"])
        
        for item in cart.items.all():
            ws.append([item.product.name, item.quantity, item.product.price, item.item_cost()])
        
        ws.append([])
        ws.append(["Итого", "", "", cart.total_cost()])
        ws.append(["Адрес доставки", address])

        buffer = BytesIO()
        wb.save(buffer)
        buffer.seek(0)

        subject = f"Ваш заказ в магазине"
        body = f"Благодарим за заказ! Чек во вложении. Адрес доставки: {address}"
        email = EmailMessage(
            subject, body, settings.EMAIL_HOST_USER, [request.user.email]
        )
        email.attach(f'receipt_{cart.id}.xlsx', buffer.getvalue(), 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        email.send()

        cart.items.all().delete()
        
        messages.success(request, "Заказ оформлен! Чек отправлен на вашу почту.")
        return redirect('catalog:product_list')

    return render(request, 'shop/checkout.html', {'cart': cart})

class ManufacturerViewSet(viewsets.ModelViewSet):
    queryset = Manufacturer.objects.all()
    serializer_class = ManufacturerSerializer
    permission_classes = [permissions.IsAuthenticated]


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticated]


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAuthenticated]


class CartViewSet(viewsets.ModelViewSet):
    queryset = Cart.objects.all()
    serializer_class = CartSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Cart.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class CartItemViewSet(viewsets.ModelViewSet):
    queryset = CartItem.objects.all() 
    serializer_class = CartItemSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return CartItem.objects.filter(cart__user=self.request.user)