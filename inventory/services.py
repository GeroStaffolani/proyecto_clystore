from django.db.models import Count, Sum, Avg, Q
from django.utils import timezone
from datetime import datetime, timedelta
from .models import Phone, Sale, Customer, Brand, PhoneModel


class InventoryService:
    """
    Servicio para lógica de negocio del inventario
    """
    
    @staticmethod
    def get_available_phones():
        """Obtiene celulares disponibles para venta"""
        return Phone.objects.filter(status='available').select_related('model__brand')
    
    @staticmethod
    def get_phones_by_status(status):
        """Obtiene celulares por estado"""
        return Phone.objects.filter(status=status).select_related('model__brand')
    
    @staticmethod
    def search_phones(query):
        """Busca celulares por múltiples criterios"""
        return Phone.objects.filter(
            Q(imei__icontains=query) |
            Q(model__name__icontains=query) |
            Q(model__brand__name__icontains=query) |
            Q(color__icontains=query)
        ).select_related('model__brand')
    
    @staticmethod
    def get_low_stock_models(threshold=5):
        """Obtiene modelos con poco stock"""
        return PhoneModel.objects.annotate(
            available_count=Count('phone', filter=Q(phone__status='available'))
        ).filter(available_count__lte=threshold)
    
    @staticmethod
    def update_phone_status(phone, new_status, user):
        """Actualiza el estado de un celular con registro de usuario"""
        old_status = phone.status
        phone.status = new_status
        phone.save()
        
        # Aquí se podría agregar un log de cambios
        return f"Estado cambiado de {old_status} a {new_status} por {user.username}"


class SalesService:
    """
    Servicio para lógica de negocio de ventas
    """
    
    @staticmethod
    def create_sale(phone, customer, sale_data, user):
        """Crea una nueva venta"""
        from .models import Sale
        
        sale = Sale.objects.create(
            phone=phone,
            customer=customer,
            sold_by=user,
            **sale_data
        )
        
        # Actualizar estado del teléfono
        phone.status = 'sold'
        phone.save()
        
        return sale
    
    @staticmethod
    def get_sales_by_period(start_date, end_date):
        """Obtiene ventas en un período específico"""
        return Sale.objects.filter(
            sale_date__range=[start_date, end_date]
        ).select_related('phone__model__brand', 'customer', 'sold_by')
    
    @staticmethod
    def get_monthly_sales(year=None, month=None):
        """Obtiene ventas del mes actual o especificado"""
        if not year or not month:
            now = timezone.now()
            year, month = now.year, now.month
        
        start_date = datetime(year, month, 1)
        if month == 12:
            end_date = datetime(year + 1, 1, 1) - timedelta(days=1)
        else:
            end_date = datetime(year, month + 1, 1) - timedelta(days=1)
        
        return SalesService.get_sales_by_period(start_date, end_date)
    
    @staticmethod
    def calculate_revenue(sales_queryset):
        """Calcula el revenue total de un conjunto de ventas"""
        return sales_queryset.aggregate(
            total_revenue=Sum('sale_price'),
            total_sales=Count('id'),
            average_sale=Avg('sale_price')
        )


class ReportService:
    """
    Servicio para generar reportes
    """
    
    @staticmethod
    def get_inventory_stats():
        """Estadísticas generales del inventario"""
        total_phones = Phone.objects.count()
        
        stats_by_status = Phone.objects.values('status').annotate(
            count=Count('id')
        ).order_by('status')
        
        stats_by_condition = Phone.objects.values('condition').annotate(
            count=Count('id')
        ).order_by('condition')
        
        stats_by_brand = Phone.objects.values('model__brand__name').annotate(
            count=Count('id')
        ).order_by('-count')[:10]
        
        return {
            'total_phones': total_phones,
            'by_status': list(stats_by_status),
            'by_condition': list(stats_by_condition),
            'by_brand': list(stats_by_brand),
        }
    
    @staticmethod
    def get_sales_stats():
        """Estadísticas de ventas"""
        total_sales = Sale.objects.count()
        total_revenue = Sale.objects.aggregate(Sum('sale_price'))['sale_price__sum'] or 0
        
        # Ventas por mes (últimos 12 meses)
        twelve_months_ago = timezone.now() - timedelta(days=365)
        monthly_sales = Sale.objects.filter(
            sale_date__gte=twelve_months_ago
        ).extra(
            select={'month': "strftime('%%Y-%%m', sale_date)"}
        ).values('month').annotate(
            count=Count('id'),
            revenue=Sum('sale_price')
        ).order_by('month')
        
        # Ventas por forma de pago
        payment_stats = Sale.objects.values('payment_method').annotate(
            count=Count('id'),
            revenue=Sum('sale_price')
        ).order_by('-count')
        
        return {
            'total_sales': total_sales,
            'total_revenue': total_revenue,
            'monthly_sales': list(monthly_sales),
            'payment_stats': list(payment_stats),
        }
    
    @staticmethod
    def get_monthly_revenue():
        """Revenue del mes actual vs mes anterior"""
        now = timezone.now()
        current_month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        
        # Mes actual
        current_month_revenue = Sale.objects.filter(
            sale_date__gte=current_month_start
        ).aggregate(Sum('sale_price'))['sale_price__sum'] or 0
        
        # Mes anterior
        if now.month == 1:
            prev_month_start = datetime(now.year - 1, 12, 1)
            prev_month_end = datetime(now.year, 1, 1) - timedelta(days=1)
        else:
            prev_month_start = datetime(now.year, now.month - 1, 1)
            prev_month_end = current_month_start - timedelta(days=1)
        
        prev_month_revenue = Sale.objects.filter(
            sale_date__range=[prev_month_start, prev_month_end]
        ).aggregate(Sum('sale_price'))['sale_price__sum'] or 0
        
        # Calcular porcentaje de cambio
        if prev_month_revenue > 0:
            change_percent = ((current_month_revenue - prev_month_revenue) / prev_month_revenue) * 100
        else:
            change_percent = 100 if current_month_revenue > 0 else 0
        
        return {
            'current_month': current_month_revenue,
            'previous_month': prev_month_revenue,
            'change_percent': round(change_percent, 2),
        }
    
    @staticmethod
    def get_top_selling_models(limit=10):
        """Modelos más vendidos"""
        return PhoneModel.objects.annotate(
            sales_count=Count('phone__sale')
        ).filter(sales_count__gt=0).order_by('-sales_count')[:limit]
    
    @staticmethod
    def get_customer_stats():
        """Estadísticas de clientes"""
        total_customers = Customer.objects.count()
        
        # Clientes con más compras
        top_customers = Customer.objects.annotate(
            purchase_count=Count('sale'),
            total_spent=Sum('sale__sale_price')
        ).filter(purchase_count__gt=0).order_by('-total_spent')[:10]
        
        return {
            'total_customers': total_customers,
            'top_customers': list(top_customers.values(
                'name', 'purchase_count', 'total_spent'
            )),
        }
