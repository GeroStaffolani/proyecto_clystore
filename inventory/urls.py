from django.urls import path
from . import views

urlpatterns = [
    # Página principal
    path('', views.home, name='home'),
    
    # Gestión de inventario
    path('inventario/nuevos/', views.inventory_new_list, name='inventory_new_list'),
    path('inventario/usados/', views.inventory_used_list, name='inventory_used_list'),
    path('inventory/', views.inventory_list, name='inventory_list'),
    path('inventory/add/', views.add_phone, name='add_phone'),
    path('inventory/<uuid:phone_id>/', views.phone_detail, name='phone_detail'),
    path('inventory/<uuid:phone_id>/edit/', views.edit_phone, name='edit_phone'),
    path('inventory/<uuid:phone_id>/delete/', views.delete_phone, name='delete_phone'),
    path('inventory/<uuid:phone_id>/comment/', views.add_comment, name='add_comment'),
    
    # Gestión de ventas
    path('sales/', views.sales_list, name='sales_list'),
    path('sales/add/<uuid:phone_id>/', views.add_sale, name='add_sale'),
    path('sales/<uuid:sale_id>/', views.sale_detail, name='sale_detail'),
    path('sales/<uuid:sale_id>/pickup/', views.mark_pickup, name='mark_pickup'),
    
    # Clientes
    path('customers/', views.customer_list, name='customer_list'),
    path('customers/add/', views.add_customer, name='add_customer'),
    path('customers/<int:customer_id>/', views.customer_detail, name='customer_detail'),
    
    # Reportes (solo admin)
    path('reports/', views.reports, name='reports'),
    
    # Búsqueda por QR/IMEI
    path('search/', views.search_phone, name='search_phone'),
    path('api/phone/<str:identifier>/', views.phone_api, name='phone_api'),
    
    # Registro de usuarios (solo admin)
    path('register/', views.register_user, name='register_user'),
]
