from django.core.management.base import BaseCommand
from inventory.models import Phone
from inventory.utils import IMEIValidator


class Command(BaseCommand):
    help = 'Valida todos los códigos IMEI en la base de datos'

    def handle(self, *args, **options):
        phones = Phone.objects.all()
        
        valid_count = 0
        invalid_count = 0
        
        for phone in phones:
            if IMEIValidator.is_valid_imei(phone.imei):
                valid_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'✓ {phone.imei} - {phone.model}')
                )
            else:
                invalid_count += 1
                self.stdout.write(
                    self.style.ERROR(f'✗ {phone.imei} - {phone.model} (INVÁLIDO)')
                )
        
        self.stdout.write(
            self.style.SUCCESS(f'\nResumen: {valid_count} válidos, {invalid_count} inválidos')
        )
        
        if invalid_count > 0:
            self.stdout.write(
                self.style.WARNING('Se encontraron IMEIs inválidos. Considera corregirlos.')
            )
