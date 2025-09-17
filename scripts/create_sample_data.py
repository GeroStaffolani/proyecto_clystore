"""
Script para crear datos de ejemplo en la base de datos
Ejecutar con: python manage.py shell < scripts/create_sample_data.py
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tienda_celulares.settings')
django.setup()

from django.contrib.auth import get_user_model
from inventory.models import Phone, Brand, PhoneModel

User = get_user_model()

def create_sample_data():
    print("Creando datos de ejemplo...")
    
    # Crear usuarios de ejemplo
    if not User.objects.filter(username='admin').exists():
        admin = User.objects.create_user(
            username='admin',
            email='admin@tienda.com',
            password='admin123',
            first_name='Administrador',
            last_name='Sistema',
            is_staff=True,
            is_superuser=True
        )
        print(f"Usuario admin creado: {admin.username}")
    
    if not User.objects.filter(username='empleado1').exists():
        empleado = User.objects.create_user(
            username='empleado1',
            email='empleado1@tienda.com',
            password='empleado123',
            first_name='Juan',
            last_name='Pérez'
        )
        print(f"Usuario empleado creado: {empleado.username}")
    
    # Crear marcas
    brands_data = [
        {'name': 'Samsung', 'is_active': True},
        {'name': 'Apple', 'is_active': True},
        {'name': 'Motorola', 'is_active': True},
        {'name': 'Xiaomi', 'is_active': True},
    ]
    
    for brand_data in brands_data:
        brand, created = Brand.objects.get_or_create(
            name=brand_data['name'],
            defaults=brand_data
        )
        if created:
            print(f"Marca creada: {brand.name}")
    
    # Crear modelos de teléfonos
    models_data = [
        {'brand': 'Samsung', 'name': 'Galaxy S23', 'base_price': 80000},
        {'brand': 'Apple', 'name': 'iPhone 14', 'base_price': 120000},
        {'brand': 'Xiaomi', 'name': 'Redmi Note 12', 'base_price': 60000},
        {'brand': 'Motorola', 'name': 'Moto G100', 'base_price': 50000},
    ]
    phone_models = []
    for model_data in models_data:
        brand = Brand.objects.get(name=model_data['brand'])
        phone_model, created = PhoneModel.objects.get_or_create(
            brand=brand,
            name=model_data['name'],
            defaults={'base_price': model_data['base_price']}
        )
        phone_models.append(phone_model)
        if created:
            print(f"Modelo creado: {phone_model.brand.name} {phone_model.name}")

    # Crear clientes
    from inventory.models import Customer, Phone, Sale, CustomUser
    customers_data = [
        {'name': 'Juan Perez', 'email': 'juan@example.com', 'phone': '111111', 'address': 'Calle Falsa 123', 'dni': '12345678'},
        {'name': 'Maria Gomez', 'email': 'maria@example.com', 'phone': '222222', 'address': 'Av. Siempre Viva 742', 'dni': '87654321'},
        {'name': 'Carlos Lopez', 'email': 'carlos@example.com', 'phone': '333333', 'address': 'San Martin 456', 'dni': '11223344'},
    ]
    customers = []
    for data in customers_data:
        customer, created = Customer.objects.get_or_create(**data)
        customers.append(customer)
        if created:
            print(f"Cliente creado: {customer.name}")

    # Crear celulares en inventario
    import random
    from decimal import Decimal
    colors = ['Negro', 'Blanco', 'Azul', 'Rojo']
    storage_options = ['64GB', '128GB', '256GB']
    admin_user = CustomUser.objects.filter(username='admin').first()
    phones = []
    for i in range(1, 11):
        model = random.choice(phone_models)
        imei = f"{random.randint(100000000000000, 999999999999999)}"[:15]
        phone, created = Phone.objects.get_or_create(
            model=model,
            imei=imei,
            status=random.choice(['available', 'reserved']),
            condition=random.choice(['new', 'used']),
            price=model.base_price + Decimal(random.randint(-5000, 5000)),
            storage_capacity=random.choice(storage_options),
            color=random.choice(colors),
            notes='',
            added_by=admin_user
        )
        phones.append(phone)
        if created:
            print(f"Celular creado: {phone.model} IMEI:{phone.imei}")

    # Crear ventas de ejemplo
    for i in range(3):
        phone = phones[i]
        customer = customers[i]
        sale, created = Sale.objects.get_or_create(
            phone=phone,
            customer=customer,
            sale_price=phone.price,
            payment_method=random.choice(['cash', 'card', 'transfer']),
            is_picked_up=True,
            sold_by=admin_user,
            notes='Venta de ejemplo'
        )
        if created:
            print(f"Venta creada: {sale}")

if __name__ == '__main__':
    create_sample_data()
    print("¡Datos de ejemplo creados exitosamente!")
