from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.http import JsonResponse, HttpResponseForbidden
from django.db.models import Q, Count, Sum, Avg
from django.utils import timezone
from django.core.paginator import Paginator
from datetime import datetime, timedelta
import json

from .models import Phone, PhoneModel, Brand, Sale, Customer, PhoneComment, CustomUser
from .forms import (
    PhoneForm, PhoneCommentForm, SaleForm, CustomerForm, 
    PhoneSearchForm, CustomUserCreationForm
)
from .services import InventoryService, SalesService, ReportService


def is_admin(user):
    """Verifica si el usuario es administrador"""
    return user.is_authenticated and user.is_admin()


@login_required
def home(request):
    """
    Página principal con resumen del sistema
    """
    # Estadísticas generales
    total_phones = Phone.objects.count()
    available_phones = Phone.objects.filter(status='available').count()
    sold_phones = Phone.objects.filter(status='sold').count()
    reserved_phones = Phone.objects.filter(status='reserved').count()
    
    # Ventas del mes actual
    current_month = timezone.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    monthly_sales = Sale.objects.filter(sale_date__gte=current_month).count()
    monthly_revenue = Sale.objects.filter(
        sale_date__gte=current_month
    ).aggregate(total=Sum('sale_price'))['total'] or 0
    
    # Últimas actividades
    recent_phones = Phone.objects.select_related('model__brand', 'added_by').order_by('-created_at')[:5]
    recent_sales = Sale.objects.select_related('phone__model__brand', 'customer', 'sold_by').order_by('-sale_date')[:5]
    
    context = {
        'total_phones': total_phones,
        'available_phones': available_phones,
        'sold_phones': sold_phones,
        'reserved_phones': reserved_phones,
        'monthly_sales': monthly_sales,
        'monthly_revenue': monthly_revenue,
        'recent_phones': recent_phones,
        'recent_sales': recent_sales,
    }
    
    return render(request, 'inventory/home.html', context)


@login_required
def inventory_list(request):
    """
    Lista de celulares en inventario con filtros y búsqueda
    """
    form = PhoneSearchForm(request.GET)
    phones = Phone.objects.select_related('model__brand', 'added_by').exclude(status='sold').order_by('-created_at')
    # Aplicar filtros
    if form.is_valid():
        search = form.cleaned_data.get('search')
        status = form.cleaned_data.get('status')
        condition = form.cleaned_data.get('condition')
        if search:
            phones = phones.filter(
                Q(imei__icontains=search) |
                Q(model__name__icontains=search) |
                Q(model__brand__name__icontains=search) |
                Q(color__icontains=search)
            )
        if status:
            phones = phones.filter(status=status)
        if condition:
            phones = phones.filter(condition=condition)
    paginator = Paginator(phones, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'form': form,
        'page_obj': page_obj,
        'phones': page_obj,
    }
    return render(request, 'inventory/inventory_list.html', context)
@login_required
def inventory_new_list(request):
    """
    Lista de celulares NUEVOS en inventario
    """
    form = PhoneSearchForm(request.GET)
    phones = Phone.objects.select_related('model__brand', 'added_by').filter(condition='new').exclude(status='sold').order_by('-created_at')
    # Aplicar filtros de búsqueda (excepto condición, ya filtrado)
    if form.is_valid():
        search = form.cleaned_data.get('search')
        status = form.cleaned_data.get('status')
        if search:
            phones = phones.filter(
                Q(imei__icontains=search) |
                Q(model__name__icontains=search) |
                Q(model__brand__name__icontains=search) |
                Q(color__icontains=search)
            )
        if status:
            phones = phones.filter(status=status)
    paginator = Paginator(phones, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'form': form,
        'page_obj': page_obj,
        'phones': page_obj,
        'inventory_type': 'Nuevos',
    }
    return render(request, 'inventory/inventory_list.html', context)

@login_required
def inventory_used_list(request):
    """
    Lista de celulares USADOS en inventario
    """
    form = PhoneSearchForm(request.GET)
    phones = Phone.objects.select_related('model__brand', 'added_by').filter(condition='used').exclude(status='sold').order_by('-created_at')
    # Aplicar filtros de búsqueda (excepto condición, ya filtrado)
    if form.is_valid():
        search = form.cleaned_data.get('search')
        status = form.cleaned_data.get('status')
        if search:
            phones = phones.filter(
                Q(imei__icontains=search) |
                Q(model__name__icontains=search) |
                Q(model__brand__name__icontains=search) |
                Q(color__icontains=search)
            )
        if status:
            phones = phones.filter(status=status)
    paginator = Paginator(phones, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'form': form,
        'page_obj': page_obj,
        'phones': page_obj,
        'inventory_type': 'Usados',
    }
    return render(request, 'inventory/inventory_list.html', context)
    """
    Lista de celulares en inventario con filtros y búsqueda
    """
    form = PhoneSearchForm(request.GET)
    phones = Phone.objects.select_related('model__brand', 'added_by').order_by('-created_at')
    
    # Aplicar filtros
    if form.is_valid():
        search = form.cleaned_data.get('search')
        status = form.cleaned_data.get('status')
        condition = form.cleaned_data.get('condition')
        
        if search:
            phones = phones.filter(
                Q(imei__icontains=search) |
                Q(model__name__icontains=search) |
                Q(model__brand__name__icontains=search) |
                Q(color__icontains=search)
            )
        
        if status:
            phones = phones.filter(status=status)
        
        if condition:
            phones = phones.filter(condition=condition)
    
    # Paginación
    paginator = Paginator(phones, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'form': form,
        'page_obj': page_obj,
        'phones': page_obj,
    }
    
    return render(request, 'inventory/inventory_list.html', context)


@login_required
def add_phone(request):
    """
    Agregar nuevo celular al inventario
    """
    if request.method == 'POST':
        form = PhoneForm(request.POST)
        if form.is_valid():
            phone = form.save(commit=False)
            phone.added_by = request.user
            phone.save()
            messages.success(request, f'Celular {phone.model} agregado exitosamente.')
            return redirect('phone_detail', phone_id=phone.id)
    else:
        form = PhoneForm()
    
    return render(request, 'inventory/add_phone.html', {'form': form})


@login_required
def phone_detail(request, phone_id):
    """
    Detalle de un celular específico
    """
    phone = get_object_or_404(Phone, id=phone_id)
    comments = phone.comments.select_related('user').order_by('-created_at')
    
    # Verificar si tiene venta asociada
    sale = None
    try:
        sale = phone.sale
    except Sale.DoesNotExist:
        pass
    
    context = {
        'phone': phone,
        'comments': comments,
        'sale': sale,
        'comment_form': PhoneCommentForm(),
    }
    
    return render(request, 'inventory/phone_detail.html', context)


@login_required
def edit_phone(request, phone_id):
    """
    Editar información de un celular
    """
    phone = get_object_or_404(Phone, id=phone_id)
    
    if request.method == 'POST':
        form = PhoneForm(request.POST, instance=phone)
        if form.is_valid():
            form.save()
            messages.success(request, 'Información del celular actualizada.')
            return redirect('phone_detail', phone_id=phone.id)
    else:
        form = PhoneForm(instance=phone)
    
    return render(request, 'inventory/edit_phone.html', {'form': form, 'phone': phone})


@login_required
@user_passes_test(is_admin)
def delete_phone(request, phone_id):
    """
    Eliminar celular (solo administradores)
    """
    phone = get_object_or_404(Phone, id=phone_id)
    
    if request.method == 'POST':
        phone_info = f"{phone.model} - {phone.imei}"
        phone.delete()
        messages.success(request, f'Celular {phone_info} eliminado exitosamente.')
        return redirect('inventory_list')
    
    return render(request, 'inventory/delete_phone.html', {'phone': phone})


@login_required
def add_comment(request, phone_id):
    """
    Agregar comentario a un celular
    """
    phone = get_object_or_404(Phone, id=phone_id)
    
    if request.method == 'POST':
        form = PhoneCommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.phone = phone
            comment.user = request.user
            comment.save()
            messages.success(request, 'Comentario agregado.')
    
    return redirect('phone_detail', phone_id=phone.id)


@login_required
def sales_list(request):
    """
    Lista de ventas
    """
    sales = Sale.objects.select_related(
        'phone__model__brand', 'customer', 'sold_by'
    ).order_by('-sale_date')
    
    # Paginación
    paginator = Paginator(sales, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'inventory/sales_list.html', {'page_obj': page_obj})


@login_required
def add_sale(request, phone_id):
    """
    Registrar venta de un celular
    """
    phone = get_object_or_404(Phone, id=phone_id)
    
    # Verificar que el celular se puede vender
    if not phone.can_be_sold():
        messages.error(request, 'Este celular no está disponible para venta.')
        return redirect('phone_detail', phone_id=phone.id)
    
    if request.method == 'POST':
        form = SaleForm(request.POST, phone=phone)
        if form.is_valid():
            sale = form.save(commit=False)
            sale.phone = phone
            sale.sold_by = request.user
            sale.save()
            messages.success(request, f'Venta registrada exitosamente.')
            return redirect('sale_detail', sale_id=sale.id)
    else:
        form = SaleForm(phone=phone)
    
    return render(request, 'inventory/add_sale.html', {'form': form, 'phone': phone})


@login_required
def sale_detail(request, sale_id):
    """
    Detalle de una venta
    """
    sale = get_object_or_404(Sale, id=sale_id)
    return render(request, 'inventory/sale_detail.html', {'sale': sale})


@login_required
def mark_pickup(request, sale_id):
    """
    Marcar venta como retirada
    """
    sale = get_object_or_404(Sale, id=sale_id)
    
    if request.method == 'POST':
        sale.is_picked_up = True
        sale.pickup_date = timezone.now()
        sale.save()
        messages.success(request, 'Venta marcada como retirada.')
    
    return redirect('sale_detail', sale_id=sale.id)


@login_required
def customer_list(request):
    """
    Lista de clientes
    """
    customers = Customer.objects.annotate(
        total_purchases=Count('sale')
    ).order_by('-created_at')
    
    # Paginación
    paginator = Paginator(customers, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'inventory/customer_list.html', {'page_obj': page_obj})


@login_required
def add_customer(request):
    """
    Agregar nuevo cliente
    """
    if request.method == 'POST':
        form = CustomerForm(request.POST)
        if form.is_valid():
            customer = form.save()
            messages.success(request, f'Cliente {customer.name} agregado exitosamente.')
            return redirect('customer_detail', customer_id=customer.id)
    else:
        form = CustomerForm()
    
    return render(request, 'inventory/add_customer.html', {'form': form})


@login_required
def customer_detail(request, customer_id):
    """
    Detalle de un cliente
    """
    customer = get_object_or_404(Customer, id=customer_id)
    sales = customer.sale_set.select_related('phone__model__brand').order_by('-sale_date')
    
    return render(request, 'inventory/customer_detail.html', {
        'customer': customer,
        'sales': sales
    })


@login_required
@user_passes_test(is_admin)
def reports(request):
    """
    Reportes del sistema (solo administradores)
    """
    # Usar el servicio de reportes
    report_service = ReportService()
    
    # Reportes básicos
    inventory_stats = report_service.get_inventory_stats()
    sales_stats = report_service.get_sales_stats()
    monthly_revenue = report_service.get_monthly_revenue()
    top_models = report_service.get_top_selling_models()
    
    context = {
        'inventory_stats': inventory_stats,
        'sales_stats': sales_stats,
        'monthly_revenue': monthly_revenue,
        'top_models': top_models,
    }
    
    return render(request, 'inventory/reports.html', context)


@login_required
def search_phone(request):
    """
    Búsqueda rápida de celulares por IMEI o código QR
    """
    query = request.GET.get('q', '').strip()
    phone = None
    
    if query:
        # Buscar por IMEI o ID
        try:
            if len(query) == 15 and query.isdigit():
                # Buscar por IMEI
                phone = Phone.objects.select_related('model__brand').get(imei=query)
            else:
                # Buscar por ID (UUID)
                phone = Phone.objects.select_related('model__brand').get(id=query)
        except Phone.DoesNotExist:
            messages.error(request, f'No se encontró ningún celular con el código: {query}')
    
    return render(request, 'inventory/search_phone.html', {
        'phone': phone,
        'query': query
    })


@login_required
def phone_api(request, identifier):
    """
    API para obtener información de un celular por IMEI o ID
    """
    try:
        if len(identifier) == 15 and identifier.isdigit():
            phone = Phone.objects.select_related('model__brand').get(imei=identifier)
        else:
            phone = Phone.objects.select_related('model__brand').get(id=identifier)
        
        data = {
            'id': str(phone.id),
            'model': str(phone.model),
            'imei': phone.imei,
            'status': phone.get_status_display(),
            'condition': phone.get_condition_display(),
            'price': str(phone.price),
            'color': phone.color,
            'storage_capacity': phone.storage_capacity,
            'added_by': phone.added_by.get_full_name() if phone.added_by else '',
            'created_at': phone.created_at.strftime('%d/%m/%Y %H:%M'),
        }
        
        return JsonResponse(data)
    
    except Phone.DoesNotExist:
        return JsonResponse({'error': 'Celular no encontrado'}, status=404)


@login_required
@user_passes_test(is_admin)
def register_user(request):
    """
    Registrar nuevo usuario (solo administradores)
    """
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, f'Usuario {user.username} creado exitosamente.')
            return redirect('home')
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'inventory/register_user.html', {'form': form})
