from django.contrib import admin
from .models import Profile, Product, Transaction, TransactionItem

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'role', 'is_active', 'created_at']
    list_filter = ['role', 'is_active']
    search_fields = ['user__username', 'user__email']

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'price', 'status', 'created_by', 'created_at']
    list_filter = ['status']
    search_fields = ['name', 'description']

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ['id', 'teller', 'customer_name', 'total_amount', 'payment_method', 'transaction_date']
    list_filter = ['payment_method', 'transaction_date']
    search_fields = ['customer_name', 'teller__username']

@admin.register(TransactionItem)
class TransactionItemAdmin(admin.ModelAdmin):
    list_display = ['transaction', 'product', 'quantity', 'price']
    list_filter = ['product']
