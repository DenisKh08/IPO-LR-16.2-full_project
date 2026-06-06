from rest_framework import permissions
from rest_framework import generics, permissions
from .models import Profile, Order
from .serializers import ProfileSerializer, OrderSerializer
from .permissions import IsAdminRole

class IsAdminOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.is_authenticated and request.user.profile.role == 'ADMIN'

# В ViewSet для заказов
def get_queryset(self):
    if self.request.user.profile.role == 'ADMIN':
        return Order.objects.all()
    return Order.objects.filter(user=self.request.user)