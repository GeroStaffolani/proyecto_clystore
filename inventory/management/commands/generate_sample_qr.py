from django.core.management.base import BaseCommand
from inventory.models import Phone
from inventory.utils import QRCodeGenerator, LabelGenerator
import os


class Command(BaseCommand):
    help = 'Genera códigos QR de ejemplo para celulares'

    def add_arguments(self, parser):
        parser.add_argument(
            '--count',
            type=int,
            default=10,
            help='Número de códigos QR a generar'
        )
        parser.add_argument(
            '--output',
            type=str,
            default='qr_codes',
            help='Directorio de salida'
        )

    def handle(self, *args, **options):
        count = options['count']
        output_dir = options['output']
        
        # Crear directorio si no existe
        os.makedirs(output_dir, exist_ok=True)
        
        phones = Phone.objects.all()[:count]
        
        if not phones:
            self.stdout.write(
                self.style.ERROR('No hay celulares en la base de datos')
            )
            return
        
        for i, phone in enumerate(phones):
            qr_data = QRCodeGenerator.generate_phone_qr_data(phone)
            qr_image = QRCodeGenerator.generate_qr_code(qr_data)
            
            # Guardar imagen (esto requeriría procesamiento adicional del base64)
            filename = f"{output_dir}/phone_{phone.id}.png"
            
            self.stdout.write(
                self.style.SUCCESS(f'QR generado para {phone.model}: {qr_data}')
            )
        
        self.stdout.write(
            self.style.SUCCESS(f'Se generaron {len(phones)} códigos QR')
        )
