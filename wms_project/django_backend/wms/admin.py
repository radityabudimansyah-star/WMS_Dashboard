from django.contrib import admin
from .models import UserProfile, SKU, InboundTruck, OutboundTruck


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display  = ['user', 'role', 'full_name', 'created_at']
    list_filter   = ['role']
    search_fields = ['user__username', 'full_name']


@admin.register(SKU)
class SKUAdmin(admin.ModelAdmin):
    list_display  = ['sku_number', 'product_name', 'cse_per_pallet', 'updated_at']
    search_fields = ['sku_number', 'product_name']


@admin.register(InboundTruck)
class InboundTruckAdmin(admin.ModelAdmin):
    list_display  = ['license_plate', 'truck_type', 'status', 'registered_by', 'created_at']
    list_filter   = ['status', 'truck_type']
    search_fields = ['license_plate']


@admin.register(OutboundTruck)
class OutboundTruckAdmin(admin.ModelAdmin):
    list_display  = ['license_plate', 'truck_type', 'destination', 'status', 'registered_by', 'created_at']
    list_filter   = ['status', 'truck_type']
    search_fields = ['license_plate', 'destination']
