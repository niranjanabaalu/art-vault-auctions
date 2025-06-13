from django.contrib import admin
from .models import Painting, Transaction, AdminPainting

# Register Painting model with custom admin class
@admin.register(Painting)
class PaintingAdmin(admin.ModelAdmin):
    list_display = ('title', 'price_range', 'start_time', 'end_time')
    search_fields = ('title', 'price_range')
    list_filter = ('start_time', 'end_time')

# Register Transaction model with custom admin class
@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('painting', 'seller', 'buyer', 'amount_paid', 'transaction_status', 'date')
    search_fields = ('painting__title', 'seller__username', 'buyer__username')  # Adjust based on related fields
    list_filter = ('transaction_status', 'date')

@admin.register(AdminPainting)
class AdminPaintingAdmin(admin.ModelAdmin):
    list_display = ('title', 'price', 'available', 'uploaded_at')
    search_fields = ('title',)
    list_filter = ('available', 'uploaded_at')