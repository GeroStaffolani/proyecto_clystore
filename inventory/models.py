from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from django.core.validators import RegexValidator
import uuid


class CustomUser(AbstractUser):
    """
    Modelo de usuario personalizado con información adicional
    """
    ROLE_CHOICES = [
        ('admin', 'Administrador'),
        ('employee', 'Empleado'),
    ]
    
    role = models.CharField(
        max_length=10,
        choices=ROLE_CHOICES,
        default='employee',
        verbose_name='Rol'
    )
    phone = models.CharField(
        max_length=20,
        blank=True,
        verbose_name='Teléfono'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Fecha de creación'
    )
    is_active_employee = models.BooleanField(
        default=True,
        verbose_name='Empleado activo'
    )
    
    class Meta:
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'
    
    def __str__(self):
        return f"{self.get_full_name()} ({self.get_role_display()})"
    
    def is_admin(self):
        return self.role == 'admin' or self.is_staff
    
    def can_delete_records(self):
        return self.is_admin()
    
    def can_access_reports(self):
        return self.is_admin()


class Brand(models.Model):
    """
    Modelo para las marcas de celulares
    """
    name = models.CharField(
        max_length=50,
        unique=True,
        verbose_name='Nombre'
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name='Activa'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Fecha de creación'
    )
    
    class Meta:
        verbose_name = 'Marca'
        verbose_name_plural = 'Marcas'
        ordering = ['name']
    
    def __str__(self):
        return self.name


class PhoneModel(models.Model):
    """
    Modelo para los modelos de celulares
    """
    brand = models.ForeignKey(
        Brand,
        on_delete=models.CASCADE,
        verbose_name='Marca'
    )
    name = models.CharField(
        max_length=100,
        verbose_name='Nombre del modelo'
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name='Activo'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Fecha de creación'
    )
    
    class Meta:
        verbose_name = 'Modelo de celular'
        verbose_name_plural = 'Modelos de celulares'
        unique_together = ['brand', 'name']
        ordering = ['brand__name', 'name']
    
    def __str__(self):
        return f"{self.brand.name} {self.name}"


class Phone(models.Model):
    internal_code = models.CharField(
        max_length=30,
        unique=True,
        blank=True,
        null=True,
        verbose_name='Código interno'
    )
    battery_percentage = models.PositiveIntegerField(
        default=100,
        verbose_name='Porcentaje de batería'
    )
    ACQUISITION_CHOICES = [
        ('mayorista', 'Compra mayorista'),
        ('parte_pago', 'Parte de pago'),
        ('', 'No aplica'),
    ]
    acquisition_type = models.CharField(
        max_length=20,
        choices=ACQUISITION_CHOICES,
        blank=True,
        default='',
        verbose_name='Tipo de adquisición'
    )
    acquired_from = models.ForeignKey(
        'Customer',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Cliente que entregó',
        help_text='Solo si fue parte de pago',
        related_name='phones_acquired'
    )
    """
    Modelo principal para los celulares en inventario
    """
    # Estados ajustados para inventario con foco en usados
    # Orden lógico: Stock -> Reservado -> Vendido -> Servicio técnico -> En camino -> Depósito
    STATUS_CHOICES = [
        ('available', 'Stock'),          # antes Disponible
        ('reserved', 'Reservado'),
        ('sold', 'Vendido'),
        ('service', 'Servicio técnico'), # nuevo (reemplaza damaged como estado operativo)
        ('in_transit', 'En camino'),
        ('warehouse', 'Depósito'),       # nuevo: almacenado fuera de sala de ventas
    ]
    
    CONDITION_CHOICES = [
        ('new', 'Nuevo'),
        ('used', 'Usado'),
        ('refurbished', 'Reacondicionado'),
        ('trade_in', 'Parte de pago'),
    ]
    
    # Validador para IMEI (15 dígitos)
    imei_validator = RegexValidator(
        regex=r'^\d{15}$',
        message='El IMEI debe tener exactamente 15 dígitos'
    )
    
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    model = models.ForeignKey(
        PhoneModel,
        on_delete=models.CASCADE,
        verbose_name='Modelo'
    )
    imei = models.CharField(
        max_length=15,
        unique=True,
        validators=[imei_validator],
        verbose_name='IMEI'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='available',
        verbose_name='Estado'
    )
    condition = models.CharField(
        max_length=20,
        choices=CONDITION_CHOICES,
        default='new',
        verbose_name='Condición'
    )
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='Precio'
    )
    storage_capacity = models.CharField(
        max_length=10,
        blank=True,
        verbose_name='Capacidad de almacenamiento'
    )
    color = models.CharField(
        max_length=30,
        blank=True,
        verbose_name='Color'
    )
    notes = models.TextField(
        blank=True,
        verbose_name='Notas'
    )
    
    # Información de seguimiento
    added_by = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        related_name='phones_added',
        verbose_name='Agregado por'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Fecha de ingreso'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Última modificación'
    )
    
    class Meta:
        verbose_name = 'Celular'
        verbose_name_plural = 'Celulares'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.model} - {self.imei} ({self.get_status_display()})"
    
    def save(self, *args, **kwargs):
        # Si no se especifica precio, usar el precio base del modelo
        if not self.price:
            self.price = self.model.base_price
        super().save(*args, **kwargs)
    
    def can_be_sold(self):
        return self.status in ['available', 'reserved']
    
    def get_qr_data(self):
        """Datos para generar código QR"""
        return f"PHONE:{self.id}:{self.imei}"


class PhoneComment(models.Model):
    """
    Comentarios en los registros de celulares
    """
    phone = models.ForeignKey(
        Phone,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Celular'
    )
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        verbose_name='Usuario'
    )
    comment = models.TextField(
        verbose_name='Comentario'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Fecha'
    )
    
    class Meta:
        verbose_name = 'Comentario'
        verbose_name_plural = 'Comentarios'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Comentario de {self.user.username} - {self.created_at.strftime('%d/%m/%Y %H:%M')}"


class Customer(models.Model):
    """
    Modelo para los clientes
    """
    name = models.CharField(
        max_length=100,
        verbose_name='Nombre completo'
    )
    email = models.EmailField(
        blank=True,
        verbose_name='Email'
    )
    phone = models.CharField(
        max_length=20,
        blank=True,
        verbose_name='Teléfono'
    )
    address = models.TextField(
        blank=True,
        verbose_name='Dirección'
    )
    dni = models.CharField(
        max_length=20,
        blank=True,
        verbose_name='DNI/Documento'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Fecha de registro'
    )
    
    class Meta:
        verbose_name = 'Cliente'
        verbose_name_plural = 'Clientes'
        ordering = ['name']
    
    def __str__(self):
        return self.name


class Sale(models.Model):
    """
    Modelo para las ventas
    """
    PAYMENT_METHODS = [
        ('cash', 'Efectivo'),
        ('card', 'Tarjeta'),
        ('transfer', 'Transferencia'),
        ('financing', 'Financiación'),
        ('mixed', 'Mixto'),
    ]
    
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    phone = models.OneToOneField(
        Phone,
        on_delete=models.CASCADE,
        verbose_name='Celular'
    )
    customer = models.ForeignKey(
        Customer,
        on_delete=models.CASCADE,
        verbose_name='Cliente'
    )
    sale_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='Precio de venta'
    )
    payment_method = models.CharField(
        max_length=20,
        choices=PAYMENT_METHODS,
        verbose_name='Forma de pago'
    )
    is_picked_up = models.BooleanField(
        default=False,
        verbose_name='Retirado'
    )
    pickup_date = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Fecha de retiro'
    )
    
    # Parte de pago
    has_trade_in = models.BooleanField(
        default=False,
        verbose_name='Tiene parte de pago'
    )
    trade_in_phone = models.ForeignKey(
        Phone,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='trade_in_sales',
        verbose_name='Celular en parte de pago'
    )
    trade_in_value = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name='Valor parte de pago'
    )
    
    # Información de seguimiento
    sold_by = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name='Vendido por'
    )
    sale_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Fecha de venta'
    )
    notes = models.TextField(
        blank=True,
        verbose_name='Notas'
    )
    
    class Meta:
        verbose_name = 'Venta'
        verbose_name_plural = 'Ventas'
        ordering = ['-sale_date']
    
    def __str__(self):
        return f"Venta {self.id} - {self.customer.name} - ${self.sale_price}"
    
    def save(self, *args, **kwargs):
        # Marcar el teléfono como vendido
        if self.phone.status != 'sold':
            self.phone.status = 'sold'
            self.phone.save()
        
        # Si se marca como retirado y no tiene fecha de retiro, asignar fecha actual
        if self.is_picked_up and not self.pickup_date:
            self.pickup_date = timezone.now()
        
        super().save(*args, **kwargs)
    
    def get_final_price(self):
        """Precio final después de descontar parte de pago"""
        if self.has_trade_in and self.trade_in_value:
            return self.sale_price - self.trade_in_value
        return self.sale_price
