from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from django.conf import settings
from django.conf.urls.static import static

router = DefaultRouter()
router.register(r'manufacturers', views.ManufacturerViewSet, basename='manufacturer')
router.register(r'categories', views.CategoryViewSet, basename='category')
router.register(r'products', views.ProductViewSet, basename='product')
router.register(r'carts', views.CartViewSet, basename='cart')
router.register(r'cart-items', views.CartItemViewSet, basename='cartitem')

app_name = 'catalog'

api_urlpatterns = [
    path('', include(router.urls)),
]

urlpatterns = [ 
    path('', views.main, name = 'main'),
    path('catalog/', views.product_list, name='product_list'),
    path('catalog/<int:pk>/', views.product_detail, name='product_detail'),
    path('checkout/', views.checkout, name='checkout'),
    path('about', views.about, name = 'about author'),
    path('shop', views.shop, name = 'aboutshop'),

    path('cart/', views.cart_view, name='cart_view'),
    path('cart/add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/update/<int:item_id>/', views.update_cart, name='update_cart'),
    path('cart/remove/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),

    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_page, name='profile_page'),
    path('profile/settings/', views.settings_page, name='settings_page'),
    
    path('api/', include(api_urlpatterns)),
    path('api/me/', views.MyProfileView.as_view(), name='api_me'),
path('api/orders/', views.OrderListView.as_view(), name='api_orders'),
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)