from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Brand, PhoneModel, Phone, PhoneComment, Customer, Sale


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'role', 'is_active_employee', 'is_staff')
    list_filter = ('role', 'is_active_employee', 'is_staff', 'is_superuser')
    search_fields = ('username', 'first_name', 'last_name', 'email')
    
    fieldsets = UserAdmin.fieldsets + (
        ('Información adicional', {
            'fields': ('role', 'phone', 'is_active_employee')
        }),
    )
    
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Información adicional', {
            'fields': ('role', 'phone', 'is_active_employee')
        }),
    )


@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('name',)


@admin.register(PhoneModel)
class PhoneModelAdmin(admin.ModelAdmin):
    list_display = ('brand', 'name', 'base_price', 'is_active', 'created_at')
    list_filter = ('brand', 'is_active', 'created_at')
    search_fields = ('name', 'brand__name')


class PhoneCommentInline(admin.TabularInline):
    model = PhoneComment
    extra = 0
    readonly_fields = ('user', 'created_at')


@admin.register(Phone)
class PhoneAdmin(admin.ModelAdmin):
    list_display = ('model', 'imei', 'status', 'condition', 'price', 'added_by', 'created_at')
    list_filter = ('status', 'condition', 'model__brand', 'created_at')
    search_fields = ('imei', 'model__name', 'model__brand__name')
    readonly_fields = ('id', 'added_by', 'created_at', 'updated_at')
    inlines = [PhoneCommentInline]
    
    def save_model(self, request, obj, form, change):
        if not change:  # Si es un nuevo objeto
            obj.added_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'phone', 'dni', 'created_at')
    search_fields = ('name', 'email', 'phone', 'dni')
    list_filter = ('created_at',)


@admin.register(Sale)
class SaleAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer', 'phone', 'sale_price', 'payment_method', 'is_picked_up', 'sold_by', 'sale_date')
    list_filter = ('payment_method', 'is_picked_up', 'has_trade_in', 'sale_date')
    search_fields = ('customer__name', 'phone__imei', 'phone__model__name')
    readonly_fields = ('id', 'sold_by', 'sale_date')
    
    def save_model(self, request, obj, form, change):
        if not change:  # Si es un nuevo objeto
            obj.sold_by = request.user
        super().save_model(request, obj, form, change)


# Configuración del sitio admin
admin.site.site_header = 'Administración - Tienda de Celulares'
admin.site.site_title = 'Tienda de Celulares'
admin.site.index_title = 'Panel de Administración'
