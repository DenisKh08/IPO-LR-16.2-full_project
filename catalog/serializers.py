from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Product, Category, Manufacturer, Cart, CartItem, Profile, Order, OrderItem


class ManufacturerSerializer(serializers.ModelSerializer):
    products_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Manufacturer
        fields = ['id', 'name', 'country', 'description', 'products_count']
        read_only_fields = ['id']
    
    def get_products_count(self, obj):
        return obj.product_set.count()


class CategorySerializer(serializers.ModelSerializer):
    products_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Category
        fields = ['id', 'name', 'description', 'products_count']
        read_only_fields = ['id']
    
    def get_products_count(self, obj):
        return obj.product_set.count()


class ProductSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    manufacturer_name = serializers.CharField(source='manufacturer.name', read_only=True)
    category_detail = CategorySerializer(source='category', read_only=True)
    manufacturer_detail = ManufacturerSerializer(source='manufacturer', read_only=True)
    in_stock = serializers.BooleanField(source='stock', read_only=True)
    
    class Meta:
        model = Product
        fields = [
            'id', 'name', 'description', 'image', 'price', 'stock',
            'category', 'manufacturer',
            'category_name', 'manufacturer_name',
            'category_detail', 'manufacturer_detail',
            'in_stock'
        ]
        read_only_fields = ['id']
        extra_kwargs = {
            'category': {'write_only': True},
            'manufacturer': {'write_only': True},
        }
    
    def validate_price(self, value):
        if value < 0:
            raise serializers.ValidationError("Цена не может быть отрицательной")
        return value
    
    def validate_stock(self, value):
        if value < 0:
            raise serializers.ValidationError("Количество на складе не может быть отрицательным")
        return value


class CartItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    product_price = serializers.DecimalField(source='product.price', max_digits=10, decimal_places=2, read_only=True)
    item_total = serializers.SerializerMethodField()
    max_available = serializers.IntegerField(source='product.stock', read_only=True)
    
    class Meta:
        model = CartItem
        fields = [
            'id', 'cart', 'product', 'quantity',
            'product_name', 'product_price', 'item_total', 'max_available'
        ]
        read_only_fields = ['id']
    
    def get_item_total(self, obj):
        return obj.item_cost()
    
    def validate_quantity(self, value):
        if value < 1:
            raise serializers.ValidationError("Количество должно быть больше 0")
        return value
    
    def validate(self, data):
        product = data.get('product')
        quantity = data.get('quantity')
        
        if product and quantity and quantity > product.stock:
            raise serializers.ValidationError(
                f"Недостаточно товара '{product.name}' на складе. Доступно: {product.stock}"
            )
        return data


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    user_username = serializers.CharField(source='user.username', read_only=True)
    total_cost = serializers.SerializerMethodField()
    items_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Cart
        fields = [
            'id', 'user', 'user_username', 'created_at',
            'items', 'items_count', 'total_cost'
        ]
        read_only_fields = ['id', 'user', 'created_at']
    
    def get_total_cost(self, obj):
        return obj.total_cost()
    
    def get_items_count(self, obj):
        return obj.items.count()


class ProductBriefSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'name', 'price', 'stock', 'image']


class ProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    email = serializers.EmailField(source='user.email', read_only=True)

    class Meta:
        model = Profile
        fields = ['id', 'username', 'email', 'role', 'full_name', 'phone', 'address']
        # Роль лучше сделать только для чтения, чтобы покупатель не прислал PATCH и не стал админом
        read_only_fields = ['id', 'role']


class OrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)

    class Meta:
        model = OrderItem
        fields = ['id', 'product_name', 'price', 'quantity']


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True, source='orderitem_set') # или related_name, если настраивали

    class Meta:
        model = Order
        fields = ['id', 'created_at', 'status', 'address', 'items']