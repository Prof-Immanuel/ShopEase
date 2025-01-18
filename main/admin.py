from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Seller, Customer, Product, Category, Cart, CartItem, Order, OrderItem


# Register Customer model with UserAdmin
class CustomerAdmin(UserAdmin):
    model = Customer
    list_display = ['username', 'phone_number', 'email', 'is_staff', 'is_active']
    list_filter = ['is_staff', 'is_active']
    search_fields = ['username', 'phone_number', 'email']
    ordering = ['username']

    # Ensure phone_number is included in forms
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('phone_number',)}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        (None, {'fields': ('phone_number',)}),
    )

admin.site.register(Customer, CustomerAdmin)
admin.site.register(Seller)
admin.site.register(Product)
admin.site.register(Category)
admin.site.register(Cart)
admin.site.register(CartItem)
admin.site.register(Order)
admin.site.register(OrderItem)