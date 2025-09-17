# Sistema de Gestión de Tienda de Celulares

Sistema web desarrollado en Django para gestionar el inventario y ventas de una tienda de celulares.

## Características

- **Gestión de Inventario**: Control completo de celulares con códigos IMEI
- **Sistema de Ventas**: Registro detallado de ventas con información del cliente
- **Control de Usuarios**: Diferentes roles (Admin/Empleado) con permisos específicos
- **Seguimiento QR/IMEI**: Identificación rápida de productos
- **Historial Completo**: Registro de todas las acciones realizadas

## Requisitos

- Python 3.8+
- Django 4.2+
- SQLite (incluido) o PostgreSQL

## Instalación

1. Instalar dependencias:
\`\`\`bash
pip install -r requirements.txt
\`\`\`

2. Ejecutar migraciones:
\`\`\`bash
python manage.py makemigrations
python manage.py migrate
\`\`\`

3. Crear datos de ejemplo:
\`\`\`bash
python manage.py shell < scripts/create_sample_data.py
\`\`\`

4. Ejecutar servidor:
\`\`\`bash
python manage.py runserver
\`\`\`

## Usuarios de Ejemplo

- **Admin**: usuario: `admin`, contraseña: `admin123`
- **Empleado**: usuario: `empleado1`, contraseña: `empleado123`

## Estructura del Proyecto

- `inventory/`: App principal con modelos, vistas y lógica de negocio
- `templates/`: Templates HTML
- `scripts/`: Scripts de utilidad y datos de ejemplo
- `static/`: Archivos estáticos (CSS, JS, imágenes)

## Funcionalidades

### Para Empleados:
- Agregar nuevos celulares al inventario
- Registrar ventas
- Consultar inventario
- Agregar comentarios a registros

### Para Administradores:
- Todas las funciones de empleado
- Eliminar registros
- Acceso a reportes
- Gestión de usuarios
- Panel de administración Django
