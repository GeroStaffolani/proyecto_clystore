from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.http import JsonResponse, HttpResponseForbidden
from django.db.models import Q, Count, Sum, Avg
from django.utils import timezone
from django.urls import reverse
from django.core.paginator import Paginator
from datetime import datetime, timedelta
import json

from .models import Phone, PhoneModel, Brand, Sale, Customer, PhoneComment, CustomUser
from .forms import (
    PhoneForm, PhoneCommentForm, SaleForm, CustomerForm, 
    PhoneSearchForm, CustomUserCreationForm, PhoneModelForm
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
    if hasattr(request.user, 'role') and request.user.role == 'employee':
        return redirect('inventory_new_list')
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
    phones = Phone.objects.select_related('model__brand', 'added_by').filter(
        condition='used'
    ).exclude(status='sold').order_by('-created_at')
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
    # Obtener parámetros del GET
    customer_id = request.GET.get('customer_id', None)
    model_id = request.GET.get('model_id', None)
    is_trade_in = request.GET.get('is_trade_in', 'false') == 'true'
    
    if request.method == 'POST':
        form = PhoneForm(request.POST)
        if form.is_valid():
            phone = form.save(commit=False)
            phone.added_by = request.user
            phone.save()
            messages.success(request, f'Celular {phone.model} agregado exitosamente.')
            return redirect('phone_detail', phone_id=phone.id)
    else:
        # Preparar valores iniciales
        initial = {}
        
        # Si viene de una parte de pago, precargar datos
        if is_trade_in:
            initial['condition'] = 'used'
            initial['acquisition_type'] = 'parte_pago'
            
            if customer_id:
                initial['acquired_from'] = customer_id
            
            if model_id:
                initial['model'] = model_id
        elif customer_id:
            # Si solo viene customer_id (de crear cliente)
            initial['acquired_from'] = customer_id
        
        form = PhoneForm(initial=initial)
    
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
    if not phone.can_be_sold():
        messages.error(request, 'Este celular no está disponible para venta.')
        return redirect('phone_detail', phone_id=phone.id)
    from .forms import SalePaymentDetailForm, SaleCardDetailForm
    payment_detail_form = None
    card_form = None
    
    # Obtener el customer_id si viene del parámetro GET (cuando regresa de crear cliente)
    customer_id = request.GET.get('customer_id', None)
    
    if request.method == 'POST':
        form = SaleForm(request.POST, phone=phone)
        payment_detail_form = SalePaymentDetailForm(request.POST)
        card_form = SaleCardDetailForm(request.POST)
        if form.is_valid() and payment_detail_form.is_valid():
            sale = form.save(commit=False)
            sale.phone = phone
            sale.sold_by = request.user

            # Procesar parte de pago (trade-in)
            if sale.has_trade_in:
                trade_in_model = form.cleaned_data.get('trade_in_model')
                trade_in_value = form.cleaned_data.get('trade_in_value')
                if trade_in_model and trade_in_value:
                    trade_in_info = f"\nParte de pago:\n"
                    trade_in_info += f"- Modelo: {trade_in_model.brand} {trade_in_model.name}\n"
                    trade_in_info += f"- Valor: ${trade_in_value:.2f}"
                    sale.notes = (sale.notes or '') + trade_in_info

            # Procesar detalles de pago con tarjeta si el método es tarjeta
            if sale.payment_method == 'card' and card_form.is_valid():
                tarjeta = card_form.cleaned_data.get('tarjeta', '')
                cuotas = card_form.cleaned_data.get('cuotas', '1')
                monto_base = card_form.cleaned_data.get('monto_base', 0)
                monto_total = card_form.cleaned_data.get('monto_total', 0)
                cotizacion = card_form.cleaned_data.get('cotizacion_dolar', 0)
                monto_usd = card_form.cleaned_data.get('monto_usd', 0)
                
                # Construir nota con información de tarjeta
                card_info = f"\nPago con Tarjeta:\n"
                card_info += f"- Tarjeta: {tarjeta}\n"
                card_info += f"- Cuotas: {cuotas}\n"
                card_info += f"- Monto base: ${monto_base:.2f}\n"
                card_info += f"- Monto total con interés: ${monto_total:.2f}\n"
                card_info += f"- Cotización USD: ${cotizacion:.2f}\n"
                card_info += f"- Total estimado USD: ${monto_usd:.2f}"
                
                sale.notes = (sale.notes or '') + card_info

            # NUEVO: procesar JSON de pagos mixtos si existe
            raw_json = request.POST.get('payment_breakdown_json', '').strip()
            payment_components = []
            parsed_ok = False
            errors = []
            if raw_json:
                try:
                    data = json.loads(raw_json)
                    if isinstance(data, list):
                        comp_index = 0
                        total_usd = 0
                        lines = []
                        for comp in data:
                            comp_index += 1
                            tipo = comp.get('tipo') or ''
                            monto = comp.get('monto')
                            moneda = comp.get('moneda') or ''
                            cotiz = comp.get('cotizacion')
                            cuotas = comp.get('cuotas')
                            tarjeta = comp.get('tarjeta')
                            # Validaciones básicas
                            if not monto or monto <= 0:
                                errors.append(f'Componente {comp_index}: monto inválido')
                                continue
                            if moneda not in ('ARS', 'USD'):
                                errors.append(f'Componente {comp_index}: moneda inválida')
                                continue
                            if moneda == 'ARS' and (not cotiz or cotiz <= 0):
                                errors.append(f'Componente {comp_index}: cotización requerida para ARS')
                                continue
                            if tipo == 'card' and not tarjeta:
                                errors.append(f'Componente {comp_index}: tarjeta requerida para pago con tarjeta')
                                continue
                            # Calcular USD estimado
                            if moneda == 'USD':
                                usd_equiv = float(monto)
                            else:
                                usd_equiv = float(monto) / float(cotiz)
                            total_usd += usd_equiv
                            detail_parts = []
                            if tipo == 'cash_ars':
                                detail_parts.append('Efectivo ARS')
                            elif tipo == 'cash_usd':
                                detail_parts.append('Efectivo USD')
                            elif tipo == 'card':
                                detail_parts.append('Tarjeta')
                            else:
                                # fallback genérico
                                detail_parts.append(tipo)
                            detail_parts.append(f"{monto} {moneda}")
                            if moneda == 'ARS':
                                detail_parts.append(f"@{cotiz}")
                            if tipo == 'card':
                                card_extra = tarjeta
                                if cuotas:
                                    card_extra += f" {cuotas} cuotas"
                                detail_parts.append(f"({card_extra})")
                            detail_parts.append(f"=> USD {usd_equiv:.2f}")
                            lines.append(f"{comp_index}) {' '.join(detail_parts)}")
                            payment_components.append({
                                'tipo': tipo,
                                'monto': monto,
                                'moneda': moneda,
                                'cotizacion': cotiz,
                                'cuotas': cuotas,
                                'tarjeta': tarjeta,
                                'usd_equiv': round(usd_equiv, 2)
                            })
                        if lines:
                            parsed_ok = True
                            header = 'Pago mixto:' if len(lines) > 1 else 'Pago:'
                            block = [header] + lines + [f"Total estimado USD: {total_usd:.2f}"]
                            # Adjuntar a notas existentes
                            extra_notes = '\n' + '\n'.join(block) + '\n[PAYMENTS_JSON] ' + json.dumps(payment_components, ensure_ascii=False)
                            sale.notes = (sale.notes or '') + extra_notes
                    else:
                        errors.append('Formato de JSON inválido')
                except json.JSONDecodeError:
                    errors.append('No se pudo parsear el JSON de pagos')
            # Si no se procesó JSON, mantener la lógica antigua mínima (por compatibilidad)
            if not parsed_ok:
                metodo = payment_detail_form.cleaned_data.get('metodo')
                if metodo == 'pesos':
                    monto = payment_detail_form.cleaned_data.get('monto_pesos')
                    cotiz = payment_detail_form.cleaned_data.get('cotizacion')
                    sale.notes = (sale.notes or '') + f"\nPago en pesos: ${monto} (Cotización USD: {cotiz})"
                elif metodo == 'mixto':
                    monto = payment_detail_form.cleaned_data.get('monto_pesos')
                    cotiz = payment_detail_form.cleaned_data.get('cotizacion')
                    sale.notes = (sale.notes or '') + f"\nPago mixto, pesos: ${monto} (Cotización USD: {cotiz})"
            sale.save()
            if errors:
                for e in errors:
                    messages.warning(request, e)
            messages.success(request, f'Venta registrada exitosamente.')
            
            # Si tiene parte de pago, redirigir a agregar celular usado con datos del cliente
            if sale.has_trade_in:
                trade_in_model = form.cleaned_data.get('trade_in_model')
                if trade_in_model:
                    # Redirigir al formulario de agregar celular usado con parámetros
                    return redirect(f"{reverse('add_phone')}?customer_id={sale.customer.id}&model_id={trade_in_model.id}&is_trade_in=true")
            
            return redirect('sale_detail', sale_id=sale.id)
    else:
        # Si viene customer_id del GET, preseleccionarlo en el formulario
        if customer_id:
            form = SaleForm(phone=phone, initial={'customer': customer_id})
        else:
            form = SaleForm(phone=phone)
        payment_detail_form = SalePaymentDetailForm()
        card_form = SaleCardDetailForm(initial={'monto_base': phone.price, 'cuotas': '1'})
    return render(request, 'inventory/add_sale.html', {
        'form': form, 
        'phone': phone, 
        'payment_detail_form': payment_detail_form,
        'card_form': card_form
    })


@login_required
def sale_detail(request, sale_id):
    """
    Detalle de una venta
    """
    sale = get_object_or_404(Sale, id=sale_id)
    payments = []
    payments_total_usd = None
    notes_display = sale.notes or ''
    if sale.notes and '[PAYMENTS_JSON]' in sale.notes:
        marker = '[PAYMENTS_JSON]'
        idx = sale.notes.rfind(marker)
        if idx != -1:
            raw_json = sale.notes[idx + len(marker):].strip()
            # recortar la parte del marcador de las notas visibles
            notes_display = (sale.notes[:idx]).rstrip()
            try:
                data = json.loads(raw_json)
                if isinstance(data, list):
                    payments = data
                    # calcular total si viene usd_equiv
                    total = 0
                    for c in payments:
                        try:
                            total += float(c.get('usd_equiv') or 0)
                        except (TypeError, ValueError):
                            pass
                    payments_total_usd = round(total, 2)
            except json.JSONDecodeError:
                # Si algo falla dejamos las notas tal cual (con el JSON crudo)
                notes_display = sale.notes
    context = {
        'sale': sale,
        'payments': payments,
        'payments_total_usd': payments_total_usd,
        'notes_display': notes_display,
    }
    return render(request, 'inventory/sale_detail.html', context)


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
    # Obtener la URL de retorno del parámetro 'next'
    next_url = request.GET.get('next', None)
    
    if request.method == 'POST':
        form = CustomerForm(request.POST)
        if form.is_valid():
            customer = form.save()
            messages.success(request, f'Cliente {customer.name} agregado exitosamente.')
            
            # Si hay una URL de retorno, redirigir allí con el ID del cliente
            if next_url:
                # Agregar el ID del cliente como parámetro para que se seleccione automáticamente
                separator = '&' if '?' in next_url else '?'
                return redirect(f'{next_url}{separator}customer_id={customer.id}')
            
            return redirect('customer_detail', customer_id=customer.id)
    else:
        form = CustomerForm()
    
    context = {
        'form': form,
        'next_url': next_url
    }
    return render(request, 'inventory/add_customer.html', context)


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


@login_required
def update_phone_status(request, phone_id):
    """Actualiza el estado de un teléfono vía AJAX (solo admin)"""
    if not request.user.is_admin():
        return HttpResponseForbidden()
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            new_status = data.get('status')
            phone = get_object_or_404(Phone, id=phone_id)
            if new_status in dict(phone.STATUS_CHOICES):
                phone.status = new_status
                phone.save(update_fields=['status'])
                return JsonResponse({'success': True, 'new_status': new_status})
            else:
                return JsonResponse({'success': False, 'error': 'Estado inválido'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    return JsonResponse({'success': False, 'error': 'Método no permitido'})

@login_required
def add_phone_model(request):
    """Permite al admin agregar un nuevo modelo de celular"""
    if not request.user.is_admin():
        return HttpResponseForbidden()
    if request.method == 'POST':
        form = PhoneModelForm(request.POST)
        if form.is_valid():
            model = form.save()
            messages.success(request, f'Modelo {model} agregado exitosamente.')
            return redirect('add_phone_model')
    else:
        form = PhoneModelForm()
    return render(request, 'inventory/add_phone_model.html', {'form': form})


@login_required
def search_customers(request):
    """
    Vista para buscar clientes via AJAX para autocompletado
    """
    if request.method == 'GET':
        query = request.GET.get('q', '').strip()
        if len(query) >= 2:  # Solo buscar si hay al menos 2 caracteres
            customers = Customer.objects.filter(
                Q(name__icontains=query) | 
                Q(email__icontains=query) | 
                Q(phone__icontains=query) |
                Q(dni__icontains=query)
            ).order_by('name')[:20]  # Limitar a 20 resultados
            
            results = []
            for customer in customers:
                results.append({
                    'id': customer.id,
                    'name': customer.name,
                    'email': customer.email or '',
                    'phone': customer.phone or '',
                    'dni': customer.dni or '',
                    'display_text': f"{customer.name} - {customer.phone or customer.email or customer.dni}"
                })
            
            return JsonResponse({'results': results})
    
    return JsonResponse({'results': []})
