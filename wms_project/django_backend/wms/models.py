"""
WMS Models
"""

from django.db import models
from django.contrib.auth.models import User


# ─── ROLE PROFILE ─────────────────────────────────────────────────────────────
class UserProfile(models.Model):
    ROLE_CHOICES = [
        ('security',       'Security'),
        ('inbound_admin',  'Inbound Admin'),
        ('outbound_admin', 'Outbound Admin'),
        ('checker',        'Checker'),
        ('picker',         'Picker'),
        ('supervisor',     'Supervisor'),
    ]

    user       = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role       = models.CharField(max_length=30, choices=ROLE_CHOICES)
    full_name  = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} — {self.get_role_display()}"


# ─── SKU MASTERLIST ───────────────────────────────────────────────────────────
class SKU(models.Model):
    sku_number    = models.CharField(max_length=50, unique=True)
    product_name  = models.CharField(max_length=200)
    cse_per_pallet = models.PositiveIntegerField(help_text="Number of cases per pallet")
    created_at    = models.DateTimeField(auto_now_add=True)
    updated_at    = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name     = 'SKU'
        verbose_name_plural = 'SKUs'
        ordering         = ['sku_number']

    def __str__(self):
        return f"{self.sku_number} — {self.product_name}"


# ─── INBOUND TRUCK ────────────────────────────────────────────────────────────
class InboundTruck(models.Model):
    TRUCK_TYPES = [
        ('Engkel',  'Engkel'),
        ('CDD',     'CDD'),
        ('Fuso',    'Fuso'),
        ('Trailer', 'Trailer'),
        ('Pickup',  'Pickup'),
    ]

    STATUS_CHOICES = [
        ('Waiting',           'Waiting'),
        ('Unloading',         'Unloading'),
        ('Loading Completed', 'Loading Completed'),
    ]

    license_plate  = models.CharField(max_length=20)
    truck_type     = models.CharField(max_length=20, choices=TRUCK_TYPES)
    status         = models.CharField(max_length=30, choices=STATUS_CHOICES, default='Waiting')
    notes          = models.TextField(blank=True)
    registered_by  = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='inbound_registrations')
    created_at     = models.DateTimeField(auto_now_add=True)
    updated_at     = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Inbound Truck'
        verbose_name_plural = 'Inbound Trucks'

    def __str__(self):
        return f"{self.license_plate} [{self.status}]"


# ─── OUTBOUND TRUCK ───────────────────────────────────────────────────────────
class OutboundTruck(models.Model):
    TRUCK_TYPES = [
        ('Engkel',  'Engkel'),
        ('CDD',     'CDD'),
        ('Fuso',    'Fuso'),
        ('Trailer', 'Trailer'),
        ('Pickup',  'Pickup'),
    ]

    STATUS_CHOICES = [
        ('Waiting',         'Waiting'),
        ('Loading',         'Loading'),
        ('Ready to Depart', 'Ready to Depart'),
        ('Departed',        'Departed'),
    ]

    license_plate  = models.CharField(max_length=20)
    truck_type     = models.CharField(max_length=20, choices=TRUCK_TYPES)
    destination    = models.CharField(max_length=200, blank=True)
    status         = models.CharField(max_length=30, choices=STATUS_CHOICES, default='Waiting')
    notes          = models.TextField(blank=True)
    registered_by  = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='outbound_registrations')
    created_at     = models.DateTimeField(auto_now_add=True)
    updated_at     = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Outbound Truck'
        verbose_name_plural = 'Outbound Trucks'

    def __str__(self):
        return f"{self.license_plate} → {self.destination} [{self.status}]"
