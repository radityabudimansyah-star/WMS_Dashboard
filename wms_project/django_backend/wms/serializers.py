"""
WMS Serializers
"""

from rest_framework import serializers
from django.contrib.auth.models import User
from .models import UserProfile, SKU, InboundTruck, OutboundTruck


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model  = UserProfile
        fields = ['role', 'full_name']


class UserSerializer(serializers.ModelSerializer):
    role      = serializers.CharField(source='profile.role',      read_only=True)
    full_name = serializers.CharField(source='profile.full_name', read_only=True)

    class Meta:
        model  = User
        fields = ['id', 'username', 'role', 'full_name']


class SKUSerializer(serializers.ModelSerializer):
    class Meta:
        model  = SKU
        fields = ['id', 'sku_number', 'product_name', 'cse_per_pallet', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']


class InboundTruckSerializer(serializers.ModelSerializer):
    registered_by_name = serializers.SerializerMethodField()

    class Meta:
        model  = InboundTruck
        fields = ['id', 'license_plate', 'truck_type', 'status', 'notes',
                  'registered_by', 'registered_by_name', 'created_at', 'updated_at']
        read_only_fields = ['registered_by', 'created_at', 'updated_at']

    def get_registered_by_name(self, obj):
        if obj.registered_by:
            profile = getattr(obj.registered_by, 'profile', None)
            return profile.full_name if profile and profile.full_name else obj.registered_by.username
        return '—'


class OutboundTruckSerializer(serializers.ModelSerializer):
    registered_by_name = serializers.SerializerMethodField()

    class Meta:
        model  = OutboundTruck
        fields = ['id', 'license_plate', 'truck_type', 'destination', 'status', 'notes',
                  'registered_by', 'registered_by_name', 'created_at', 'updated_at']
        read_only_fields = ['registered_by', 'created_at', 'updated_at']

    def get_registered_by_name(self, obj):
        if obj.registered_by:
            profile = getattr(obj.registered_by, 'profile', None)
            return profile.full_name if profile and profile.full_name else obj.registered_by.username
        return '—'
