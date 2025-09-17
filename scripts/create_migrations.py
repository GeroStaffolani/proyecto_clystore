"""
Script para crear y aplicar migraciones
Ejecutar con: python manage.py shell < scripts/create_migrations.py
"""

import os
import sys
import django
from django.core.management import execute_from_command_line

# Add the project root to the Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tienda_celulares.settings')
django.setup()

def create_and_apply_migrations():
    print("Creando migraciones...")
    
    # Crear migraciones
    execute_from_command_line(['manage.py', 'makemigrations'])
    
    # Aplicar migraciones
    execute_from_command_line(['manage.py', 'migrate'])
    
    print("Migraciones aplicadas exitosamente!")

if __name__ == '__main__':
    create_and_apply_migrations()
