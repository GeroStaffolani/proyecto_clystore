from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser, Phone, PhoneComment, Customer, Sale, PhoneModel


class CustomUserCreationForm(UserCreationForm):
    """
    Formulario personalizado para crear usuarios
    """
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    
    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'first_name', 'last_name', 'role', 'phone')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Agregar clases CSS de Bootstrap
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
        
        # Personalizar labels
        self.fields['username'].label = 'Nombre de usuario'
        self.fields['email'].label = 'Correo electrónico'
        self.fields['first_name'].label = 'Nombre'
        self.fields['last_name'].label = 'Apellido'
        self.fields['role'].label = 'Rol'
        self.fields['phone'].label = 'Teléfono'
        self.fields['password1'].label = 'Contraseña'
        self.fields['password2'].label = 'Confirmar contraseña'


class PhoneForm(forms.ModelForm):
    """
    Formulario para agregar/editar celulares
    """
    class Meta:
        model = Phone
        fields = [
            'internal_code', 'model', 'imei', 'condition', 'price', 'storage_capacity', 'color',
            'battery_percentage', 'acquisition_type', 'acquired_from', 'notes'
        ]
        widgets = {
            'notes': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Agregar clases CSS de Bootstrap
        for field_name, field in self.fields.items():
            if isinstance(field.widget, forms.Textarea):
                field.widget.attrs['class'] = 'form-control'
            else:
                field.widget.attrs['class'] = 'form-control'

        # Personalizar labels
        self.fields['internal_code'].label = 'Código interno'
        self.fields['model'].label = 'Modelo'
        self.fields['imei'].label = 'IMEI'
        self.fields['condition'].label = 'Condición'
        self.fields['price'].label = 'Precio'
        self.fields['storage_capacity'].label = 'Almacenamiento'
        self.fields['color'].label = 'Color'
        self.fields['battery_percentage'].label = 'Porcentaje de batería'
        self.fields['acquisition_type'].label = 'Tipo de adquisición'
        self.fields['acquired_from'].label = 'Cliente que entregó'
        self.fields['notes'].label = 'Notas'
        # Placeholder para IMEI
        self.fields['imei'].widget.attrs['placeholder'] = '15 dígitos'
        self.fields['storage_capacity'].widget.attrs['placeholder'] = 'ej: 128GB'
        self.fields['color'].widget.attrs['placeholder'] = 'ej: Negro'


class PhoneCommentForm(forms.ModelForm):
    """
    Formulario para agregar comentarios a celulares
    """
    class Meta:
        model = PhoneComment
        fields = ['comment']
        widgets = {
            'comment': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['comment'].label = 'Comentario'


class CustomerForm(forms.ModelForm):
    """
    Formulario para clientes
    """
    class Meta:
        model = Customer
        fields = ['name', 'email', 'phone', 'address', 'dni']
        widgets = {
            'address': forms.Textarea(attrs={'rows': 2}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Agregar clases CSS de Bootstrap
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
        
        # Personalizar labels
        self.fields['name'].label = 'Nombre completo'
        self.fields['email'].label = 'Correo electrónico'
        self.fields['phone'].label = 'Teléfono'
        self.fields['address'].label = 'Dirección'
        self.fields['dni'].label = 'DNI/Documento'


class SaleForm(forms.ModelForm):
    """
    Formulario para registrar ventas
    """
    class Meta:
        model = Sale
        fields = [
            'customer', 'sale_price', 'payment_method', 'is_picked_up',
            'has_trade_in', 'trade_in_phone', 'trade_in_value', 'notes'
        ]
        widgets = {
            'notes': forms.Textarea(attrs={'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        phone = kwargs.pop('phone', None)
        super().__init__(*args, **kwargs)
        
        # Agregar clases CSS de Bootstrap
        for field_name, field in self.fields.items():
            if isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs['class'] = 'form-check-input'
            else:
                field.widget.attrs['class'] = 'form-control'
        
        # Si se proporciona un teléfono, establecer el precio por defecto
        if phone:
            self.fields['sale_price'].initial = phone.price
        
        # Filtrar teléfonos para parte de pago (solo disponibles y usados)
        self.fields['trade_in_phone'].queryset = Phone.objects.filter(
            status='available',
            condition__in=['used', 'trade_in']
        )
        
        # Personalizar labels
        self.fields['customer'].label = 'Cliente'
        self.fields['sale_price'].label = 'Precio de venta'
        self.fields['payment_method'].label = 'Forma de pago'
        self.fields['is_picked_up'].label = 'Retirado'
        self.fields['has_trade_in'].label = 'Tiene parte de pago'
        self.fields['trade_in_phone'].label = 'Celular en parte de pago'
        self.fields['trade_in_value'].label = 'Valor parte de pago'
        self.fields['notes'].label = 'Notas'


class PhoneSearchForm(forms.Form):
    """
    Formulario para buscar celulares
    """
    search = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Buscar por IMEI, modelo o marca...'
        }),
        label='Buscar'
    )
    status = forms.ChoiceField(
        choices=[('', 'Todos los estados')] + Phone.STATUS_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'}),
        label='Estado'
    )
    condition = forms.ChoiceField(
        choices=[('', 'Todas las condiciones')] + Phone.CONDITION_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'}),
        label='Condición'
    )


class PhoneModelForm(forms.ModelForm):
    class Meta:
        model = PhoneModel
        fields = ['brand', 'name', 'base_price', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'base_price': forms.NumberInput(attrs={'class': 'form-control'}),
            'brand': forms.Select(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Personalizar labels
        self.fields['brand'].label = 'Marca'
        self.fields['name'].label = 'Nombre del modelo'
        self.fields['base_price'].label = 'Precio base'
        self.fields['is_active'].label = '¿Está activo?'
