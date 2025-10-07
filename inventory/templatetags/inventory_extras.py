from django import template
from django.utils.safestring import mark_safe
from ..utils import QRCodeGenerator, IMEIValidator
import json

register = template.Library()


@register.filter
def generate_qr(data, size="200x200"):
    """
    Genera un código QR como imagen base64
    """
    try:
        width, height = map(int, size.split('x'))
        qr_image = QRCodeGenerator.generate_qr_code(data, (width, height))
        return mark_safe(qr_image)
    except:
        return ""


@register.filter
def format_imei(imei):
    """
    Formatea un IMEI para mostrar de manera legible
    """
    return IMEIValidator.format_imei(imei)


@register.filter
def validate_imei(imei):
    """
    Valida si un IMEI es correcto
    """
    return IMEIValidator.is_valid_imei(imei)


@register.simple_tag
def phone_qr_data(phone):
    """
    Genera los datos del QR para un celular
    """
    return QRCodeGenerator.generate_phone_qr_data(phone)


@register.simple_tag
def sale_qr_data(sale):
    """
    Genera los datos del QR para una venta
    """
    return QRCodeGenerator.generate_sale_qr_data(sale)


@register.filter
def to_json(value):
    """
    Convierte un valor a JSON para usar en JavaScript
    """
    return mark_safe(json.dumps(value))


@register.inclusion_tag('inventory/partials/qr_code.html')
def qr_code(data, size=150, label=""):
    """
    Renderiza un código QR con etiqueta
    """
    return {
        'qr_data': data,
        'size': size,
        'label': label
    }


@register.inclusion_tag('inventory/partials/phone_status_badge.html')
def phone_status_badge(phone):
    """
    Renderiza un badge del estado del celular
    """
    status_colors = {
        # Colores optimizados estilo Bootstrap para estados actuales
        'available': 'success',        # Stock - verde
        'reserved': 'info',            # Reservado - celeste
        'sold': 'warning',             # Vendido - amarillo
        'service': 'danger',           # Servicio técnico - rojo
        'in_transit': 'secondary',     # En camino - gris
        'warehouse': 'dark',           # Depósito - gris oscuro
        'damaged': 'danger',           # Legacy / fallback
    }
    
    return {
        'phone': phone,
        'color': status_colors.get(phone.status, 'secondary')
    }


@register.inclusion_tag('inventory/partials/condition_badge.html')
def condition_badge(phone):
    """
    Renderiza un badge de la condición del celular
    """
    condition_colors = {
        'new': 'primary',
        'used': 'warning',
        'refurbished': 'info',
        'trade_in': 'secondary'
    }
    
    return {
        'phone': phone,
        'color': condition_colors.get(phone.condition, 'secondary')
    }
