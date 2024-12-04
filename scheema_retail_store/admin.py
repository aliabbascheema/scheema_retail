from django.contrib import admin
from .models import Cart, CartItem, Product, Category, Order, OrderItem, Review

admin.site.register(Category)
admin.site.register(Product)
admin.site.register(Review)
admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(Cart)
admin.site.register(CartItem)