"""
WMS API Views — with automatic Google Sheets sync
"""

import threading
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate

from .models import UserProfile, SKU, InboundTruck, OutboundTruck
from .serializers import (
    UserSerializer, SKUSerializer,
    InboundTruckSerializer, OutboundTruckSerializer
)
from . import sheets_sync


def get_role(user):
    try:
        return user.profile.role
    except Exception:
        return None


def has_role(user, *roles):
    return get_role(user) in roles


def sync_in_background(sync_fn):
    thread = threading.Thread(target=sync_fn, daemon=True)
    thread.start()


@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    username = request.data.get('username', '').strip()
    password = request.data.get('password', '').strip()
    user = authenticate(username=username, password=password)
    if not user:
        return Response({'error': 'Invalid username or password.'}, status=status.HTTP_401_UNAUTHORIZED)
    token, _ = Token.objects.get_or_create(user=user)
    role      = get_role(user)
    full_name = getattr(getattr(user, 'profile', None), 'full_name', user.username)
    return Response({'token': token.key, 'user_id': user.id, 'username': user.username, 'role': role, 'full_name': full_name})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_view(request):
    try:
        request.user.auth_token.delete()
    except Exception:
        pass
    return Response({'message': 'Logged out successfully.'})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def me_view(request):
    return Response(UserSerializer(request.user).data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def sku_list(request):
    skus   = SKU.objects.all()
    search = request.query_params.get('search', '').strip()
    if search:
        skus = (skus.filter(sku_number__icontains=search) | skus.filter(product_name__icontains=search)).distinct()
    return Response(SKUSerializer(skus, many=True).data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def sku_create(request):
    if not has_role(request.user, 'inbound_admin', 'supervisor'):
        return Response({'error': 'Permission denied.'}, status=status.HTTP_403_FORBIDDEN)
    serializer = SKUSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        sync_in_background(sheets_sync.sync_sku)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def sku_detail(request, pk):
    try:
        sku = SKU.objects.get(pk=pk)
    except SKU.DoesNotExist:
        return Response({'error': 'SKU not found.'}, status=status.HTTP_404_NOT_FOUND)
    if request.method == 'GET':
        return Response(SKUSerializer(sku).data)
    if not has_role(request.user, 'inbound_admin', 'supervisor'):
        return Response({'error': 'Permission denied.'}, status=status.HTTP_403_FORBIDDEN)
    if request.method == 'PUT':
        serializer = SKUSerializer(sku, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            sync_in_background(sheets_sync.sync_sku)
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    if request.method == 'DELETE':
        sku.delete()
        sync_in_background(sheets_sync.sync_sku)
        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def inbound_list(request):
    if not has_role(request.user, 'security', 'inbound_admin', 'supervisor', 'checker'):
        return Response({'error': 'Permission denied.'}, status=status.HTTP_403_FORBIDDEN)
    trucks = InboundTruck.objects.select_related('registered_by__profile').all()
    return Response(InboundTruckSerializer(trucks, many=True).data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def inbound_create(request):
    if not has_role(request.user, 'security', 'inbound_admin', 'supervisor'):
        return Response({'error': 'Permission denied.'}, status=status.HTTP_403_FORBIDDEN)
    serializer = InboundTruckSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save(registered_by=request.user)
        sync_in_background(sheets_sync.sync_inbound)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def inbound_detail(request, pk):
    try:
        truck = InboundTruck.objects.get(pk=pk)
    except InboundTruck.DoesNotExist:
        return Response({'error': 'Not found.'}, status=status.HTTP_404_NOT_FOUND)
    if request.method == 'GET':
        return Response(InboundTruckSerializer(truck).data)
    if not has_role(request.user, 'inbound_admin', 'supervisor'):
        return Response({'error': 'Permission denied.'}, status=status.HTTP_403_FORBIDDEN)
    if request.method == 'PUT':
        serializer = InboundTruckSerializer(truck, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            sync_in_background(sheets_sync.sync_inbound)
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    if request.method == 'DELETE':
        truck.delete()
        sync_in_background(sheets_sync.sync_inbound)
        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def outbound_list(request):
    if not has_role(request.user, 'security', 'outbound_admin', 'supervisor', 'picker'):
        return Response({'error': 'Permission denied.'}, status=status.HTTP_403_FORBIDDEN)
    trucks = OutboundTruck.objects.select_related('registered_by__profile').all()
    return Response(OutboundTruckSerializer(trucks, many=True).data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def outbound_create(request):
    if not has_role(request.user, 'security', 'outbound_admin', 'supervisor'):
        return Response({'error': 'Permission denied.'}, status=status.HTTP_403_FORBIDDEN)
    serializer = OutboundTruckSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save(registered_by=request.user)
        sync_in_background(sheets_sync.sync_outbound)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def outbound_detail(request, pk):
    try:
        truck = OutboundTruck.objects.get(pk=pk)
    except OutboundTruck.DoesNotExist:
        return Response({'error': 'Not found.'}, status=status.HTTP_404_NOT_FOUND)
    if request.method == 'GET':
        return Response(OutboundTruckSerializer(truck).data)
    if not has_role(request.user, 'outbound_admin', 'supervisor'):
        return Response({'error': 'Permission denied.'}, status=status.HTTP_403_FORBIDDEN)
    if request.method == 'PUT':
        serializer = OutboundTruckSerializer(truck, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            sync_in_background(sheets_sync.sync_outbound)
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    if request.method == 'DELETE':
        truck.delete()
        sync_in_background(sheets_sync.sync_outbound)
        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard_stats(request):
    inbound  = InboundTruck.objects.all()
    outbound = OutboundTruck.objects.all()
    return Response({
        'inbound': {
            'total': inbound.count(),
            'waiting': inbound.filter(status='Waiting').count(),
            'unloading': inbound.filter(status='Unloading').count(),
            'loading_completed': inbound.filter(status='Loading Completed').count(),
        },
        'outbound': {
            'total': outbound.count(),
            'waiting': outbound.filter(status='Waiting').count(),
            'loading': outbound.filter(status='Loading').count(),
            'ready_to_depart': outbound.filter(status='Ready to Depart').count(),
            'departed': outbound.filter(status='Departed').count(),
        },
        'sku_count': SKU.objects.count(),
    })
