from django.urls import path
from .views import *

urlpatterns = [
    path('', catalog_view, name = "main")
]