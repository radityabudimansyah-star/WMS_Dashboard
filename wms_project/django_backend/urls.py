"""
WMS URL Configuration
"""

from django.contrib import admin
from django.urls import path
from wms import views

urlpatterns = [
    path('admin/', admin.site.urls),

    # Auth
    path('api/auth/login/',  views.login_view),
    path('api/auth/logout/', views.logout_view),
    path('api/auth/me/',     views.me_view),

    # Dashboard
    path('api/dashboard/',   views.dashboard_stats),

    # SKU
    path('api/sku/',         views.sku_list),
    path('api/sku/create/',  views.sku_create),
    path('api/sku/<int:pk>/', views.sku_detail),

    # Inbound
    path('api/inbound/',            views.inbound_list),
    path('api/inbound/create/',     views.inbound_create),
    path('api/inbound/<int:pk>/',   views.inbound_detail),

    # Outbound
    path('api/outbound/',           views.outbound_list),
    path('api/outbound/create/',    views.outbound_create),
    path('api/outbound/<int:pk>/',  views.outbound_detail),
]
