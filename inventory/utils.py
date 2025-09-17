import qrcode
from io import BytesIO
import base64
from PIL import Image, ImageDraw, ImageFont
from django.http import HttpResponse
from django.template.loader import render_to_string
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.units import mm
from reportlab.graphics.shapes import Drawing
from reportlab.graphics.barcode.qr import QrCodeWidget
from reportlab.graphics.renderPDF import drawToString
from reportlab.graphics import renderPDF
import uuid


class QRCodeGenerator:
    """
    Utilidad para generar códigos QR para celulares
    """
    
    @staticmethod
    def generate_qr_code(data, size=(200, 200)):
        """
        Genera un código QR y lo retorna como imagen base64
        """
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(data)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        img = img.resize(size, Image.Resampling.LANCZOS)
        
        # Convertir a base64
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        img_str = base64.b64encode(buffer.getvalue()).decode()
        
        return f"data:image/png;base64,{img_str}"
    
    @staticmethod
    def generate_phone_qr_data(phone):
        """
        Genera los datos del QR para un celular específico
        """
        return f"PHONE:{phone.id}:{phone.imei}:{phone.model.brand.name}:{phone.model.name}"
    
    @staticmethod
    def generate_sale_qr_data(sale):
        """
        Genera los datos del QR para una venta específica
        """
        return f"SALE:{sale.id}:{sale.customer.name}:{sale.sale_price}:{sale.sale_date.strftime('%Y%m%d')}"


class LabelGenerator:
    """
    Utilidad para generar etiquetas imprimibles con códigos QR
    """
    
    @staticmethod
    def generate_phone_label_pdf(phone):
        """
        Genera una etiqueta PDF para un celular
        """
        buffer = BytesIO()
        p = canvas.Canvas(buffer, pagesize=(60*mm, 40*mm))
        
        # Información del celular
        p.setFont("Helvetica-Bold", 8)
        p.drawString(5*mm, 35*mm, f"{phone.model.brand.name}")
        p.drawString(5*mm, 32*mm, f"{phone.model.name}")
        
        p.setFont("Helvetica", 6)
        p.drawString(5*mm, 28*mm, f"IMEI: {phone.imei}")
        p.drawString(5*mm, 25*mm, f"${phone.price}")
        
        if phone.color:
            p.drawString(5*mm, 22*mm, f"Color: {phone.color}")
        
        if phone.storage_capacity:
            p.drawString(5*mm, 19*mm, f"{phone.storage_capacity}")
        
        # Código QR
        qr_data = QRCodeGenerator.generate_phone_qr_data(phone)
        qr_widget = QrCodeWidget(qr_data)
        qr_widget.barWidth = 15*mm
        qr_widget.barHeight = 15*mm
        
        drawing = Drawing(15*mm, 15*mm)
        drawing.add(qr_widget)
        
        renderPDF.draw(drawing, p, 40*mm, 20*mm)
        
        p.showPage()
        p.save()
        
        buffer.seek(0)
        return buffer
    
    @staticmethod
    def generate_multiple_labels_pdf(phones):
        """
        Genera múltiples etiquetas en un PDF
        """
        buffer = BytesIO()
        p = canvas.Canvas(buffer, pagesize=A4)
        
        # Configuración de la página
        labels_per_row = 3
        labels_per_col = 7
        label_width = 60*mm
        label_height = 40*mm
        margin_x = 15*mm
        margin_y = 15*mm
        
        x_positions = [margin_x + i * (label_width + 5*mm) for i in range(labels_per_row)]
        y_positions = [A4[1] - margin_y - (i + 1) * (label_height + 2*mm) for i in range(labels_per_col)]
        
        phone_index = 0
        
        for phone in phones:
            if phone_index >= labels_per_row * labels_per_col:
                p.showPage()
                phone_index = 0
            
            row = phone_index // labels_per_row
            col = phone_index % labels_per_row
            
            x = x_positions[col]
            y = y_positions[row]
            
            # Dibujar borde de la etiqueta
            p.rect(x, y, label_width, label_height)
            
            # Información del celular
            p.setFont("Helvetica-Bold", 8)
            p.drawString(x + 2*mm, y + label_height - 5*mm, f"{phone.model.brand.name}")
            p.drawString(x + 2*mm, y + label_height - 8*mm, f"{phone.model.name}")
            
            p.setFont("Helvetica", 6)
            p.drawString(x + 2*mm, y + label_height - 12*mm, f"IMEI: {phone.imei}")
            p.drawString(x + 2*mm, y + label_height - 15*mm, f"${phone.price}")
            
            if phone.color:
                p.drawString(x + 2*mm, y + label_height - 18*mm, f"Color: {phone.color}")
            
            # Código QR
            qr_data = QRCodeGenerator.generate_phone_qr_data(phone)
            qr_widget = QrCodeWidget(qr_data)
            qr_widget.barWidth = 12*mm
            qr_widget.barHeight = 12*mm
            
            drawing = Drawing(12*mm, 12*mm)
            drawing.add(qr_widget)
            
            renderPDF.draw(drawing, p, x + label_width - 15*mm, y + 2*mm)
            
            phone_index += 1
        
        p.showPage()
        p.save()
        
        buffer.seek(0)
        return buffer


class IMEIValidator:
    """
    Utilidad para validar códigos IMEI
    """
    
    @staticmethod
    def is_valid_imei(imei):
        """
        Valida un código IMEI usando el algoritmo Luhn
        """
        if not imei or len(imei) != 15 or not imei.isdigit():
            return False
        
        # Algoritmo Luhn para validar IMEI
        def luhn_checksum(card_num):
            def digits_of(n):
                return [int(d) for d in str(n)]
            
            digits = digits_of(card_num)
            odd_digits = digits[-1::-2]
            even_digits = digits[-2::-2]
            checksum = sum(odd_digits)
            for d in even_digits:
                checksum += sum(digits_of(d*2))
            return checksum % 10
        
        return luhn_checksum(imei) == 0
    
    @staticmethod
    def format_imei(imei):
        """
        Formatea un IMEI para mostrar de manera legible
        """
        if len(imei) == 15:
            return f"{imei[:2]} {imei[2:8]} {imei[8:14]} {imei[14]}"
        return imei
    
    @staticmethod
    def get_imei_info(imei):
        """
        Extrae información básica del IMEI
        """
        if not IMEIValidator.is_valid_imei(imei):
            return None
        
        tac = imei[:8]  # Type Allocation Code
        snr = imei[8:14]  # Serial Number
        cd = imei[14]  # Check Digit
        
        return {
            'tac': tac,
            'serial_number': snr,
            'check_digit': cd,
            'formatted': IMEIValidator.format_imei(imei)
        }


class SearchHelper:
    """
    Utilidad para búsquedas avanzadas
    """
    
    @staticmethod
    def parse_search_query(query):
        """
        Analiza una consulta de búsqueda y determina el tipo
        """
        query = query.strip()
        
        # Verificar si es un IMEI
        if len(query) == 15 and query.isdigit():
            return {
                'type': 'imei',
                'value': query,
                'is_valid': IMEIValidator.is_valid_imei(query)
            }
        
        # Verificar si es un UUID (ID de celular)
        try:
            uuid.UUID(query)
            return {
                'type': 'uuid',
                'value': query,
                'is_valid': True
            }
        except ValueError:
            pass
        
        # Verificar si es un código QR de celular
        if query.startswith('PHONE:'):
            parts = query.split(':')
            if len(parts) >= 3:
                return {
                    'type': 'qr_phone',
                    'value': parts[1],  # UUID del celular
                    'imei': parts[2] if len(parts) > 2 else None,
                    'is_valid': True
                }
        
        # Verificar si es un código QR de venta
        if query.startswith('SALE:'):
            parts = query.split(':')
            if len(parts) >= 2:
                return {
                    'type': 'qr_sale',
                    'value': parts[1],  # UUID de la venta
                    'is_valid': True
                }
        
        # Búsqueda de texto general
        return {
            'type': 'text',
            'value': query,
            'is_valid': True
        }
    
    @staticmethod
    def search_phones_by_query(query):
        """
        Busca celulares basado en una consulta
        """
        from .models import Phone
        from django.db.models import Q
        
        parsed = SearchHelper.parse_search_query(query)
        
        if parsed['type'] == 'imei':
            return Phone.objects.filter(imei=parsed['value'])
        
        elif parsed['type'] == 'uuid':
            return Phone.objects.filter(id=parsed['value'])
        
        elif parsed['type'] == 'qr_phone':
            return Phone.objects.filter(id=parsed['value'])
        
        elif parsed['type'] == 'text':
            return Phone.objects.filter(
                Q(imei__icontains=query) |
                Q(model__name__icontains=query) |
                Q(model__brand__name__icontains=query) |
                Q(color__icontains=query) |
                Q(storage_capacity__icontains=query)
            )
        
        return Phone.objects.none()


class ReportGenerator:
    """
    Utilidad para generar reportes en PDF
    """
    
    @staticmethod
    def generate_inventory_report(phones):
        """
        Genera un reporte de inventario en PDF
        """
        buffer = BytesIO()
        p = canvas.Canvas(buffer, pagesize=A4)
        
        # Título
        p.setFont("Helvetica-Bold", 16)
        p.drawString(50, 800, "Reporte de Inventario")
        
        # Fecha
        from django.utils import timezone
        p.setFont("Helvetica", 10)
        p.drawString(50, 780, f"Generado: {timezone.now().strftime('%d/%m/%Y %H:%M')}")
        
        # Encabezados
        y = 750
        p.setFont("Helvetica-Bold", 10)
        p.drawString(50, y, "Marca")
        p.drawString(150, y, "Modelo")
        p.drawString(250, y, "IMEI")
        p.drawString(350, y, "Estado")
        p.drawString(420, y, "Precio")
        p.drawString(480, y, "Fecha")
        
        # Línea separadora
        p.line(50, y-5, 550, y-5)
        
        # Datos
        y -= 20
        p.setFont("Helvetica", 8)
        
        for phone in phones:
            if y < 50:  # Nueva página si es necesario
                p.showPage()
                y = 800
                p.setFont("Helvetica", 8)
            
            p.drawString(50, y, phone.model.brand.name[:15])
            p.drawString(150, y, phone.model.name[:15])
            p.drawString(250, y, phone.imei)
            p.drawString(350, y, phone.get_status_display())
            p.drawString(420, y, f"${phone.price}")
            p.drawString(480, y, phone.created_at.strftime('%d/%m/%Y'))
            
            y -= 15
        
        p.showPage()
        p.save()
        
        buffer.seek(0)
        return buffer
    
    @staticmethod
    def generate_sales_report(sales):
        """
        Genera un reporte de ventas en PDF
        """
        buffer = BytesIO()
        p = canvas.Canvas(buffer, pagesize=A4)
        
        # Título
        p.setFont("Helvetica-Bold", 16)
        p.drawString(50, 800, "Reporte de Ventas")
        
        # Fecha
        from django.utils import timezone
        p.setFont("Helvetica", 10)
        p.drawString(50, 780, f"Generado: {timezone.now().strftime('%d/%m/%Y %H:%M')}")
        
        # Encabezados
        y = 750
        p.setFont("Helvetica-Bold", 10)
        p.drawString(50, y, "Fecha")
        p.drawString(120, y, "Cliente")
        p.drawString(220, y, "Celular")
        p.drawString(320, y, "Precio")
        p.drawString(380, y, "Pago")
        p.drawString(450, y, "Estado")
        
        # Línea separadora
        p.line(50, y-5, 550, y-5)
        
        # Datos
        y -= 20
        p.setFont("Helvetica", 8)
        total_revenue = 0
        
        for sale in sales:
            if y < 50:  # Nueva página si es necesario
                p.showPage()
                y = 800
                p.setFont("Helvetica", 8)
            
            p.drawString(50, y, sale.sale_date.strftime('%d/%m/%Y'))
            p.drawString(120, y, sale.customer.name[:15])
            p.drawString(220, y, f"{sale.phone.model.brand.name} {sale.phone.model.name}"[:15])
            p.drawString(320, y, f"${sale.sale_price}")
            p.drawString(380, y, sale.get_payment_method_display()[:10])
            p.drawString(450, y, "Retirado" if sale.is_picked_up else "Pendiente")
            
            total_revenue += float(sale.sale_price)
            y -= 15
        
        # Total
        y -= 10
        p.line(320, y, 450, y)
        y -= 15
        p.setFont("Helvetica-Bold", 10)
        p.drawString(320, y, f"Total: ${total_revenue:.2f}")
        
        p.showPage()
        p.save()
        
        buffer.seek(0)
        return buffer
