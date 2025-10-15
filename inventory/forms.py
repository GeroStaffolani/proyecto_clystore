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

        # Ocultar y no requerir 'battery_percentage' si es nuevo
        condition_value = self.data.get('condition') or self.initial.get('condition') or self.fields['condition'].initial
        if condition_value == 'new':
            self.fields['battery_percentage'].required = False
            self.fields['battery_percentage'].widget = forms.HiddenInput()
        else:
            self.fields['battery_percentage'].required = True

        # El campo siempre está presente, solo es obligatorio si corresponde
        self.fields['acquired_from'].widget.attrs['class'] = 'form-control'
        if condition_value in ['used', 'trade_in']:
            self.fields['acquired_from'].required = True
        else:
            self.fields['acquired_from'].required = False

    def clean(self):
        cleaned_data = super().clean()
        condition = cleaned_data.get('condition')
        battery_percentage = cleaned_data.get('battery_percentage')
        acquired_from = cleaned_data.get('acquired_from')
        if condition == 'used' and battery_percentage in [None, '']:
            self.add_error('battery_percentage', 'Este campo es obligatorio para celulares usados.')
        if condition in ['used', 'trade_in'] and not acquired_from:
            self.add_error('acquired_from', 'Debes seleccionar el cliente que entregó el celular.')
        return cleaned_data


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
        fields = ['brand', 'name', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'brand': forms.Select(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Personalizar labels
        self.fields['brand'].label = 'Marca'
        self.fields['name'].label = 'Nombre del modelo'
        self.fields['is_active'].label = '¿Está activo?'


class SalePaymentDetailForm(forms.Form):
    monto_pesos = forms.DecimalField(
        max_digits=12,
        decimal_places=2,
        required=False,
        label='Monto abonado en pesos',
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Ej: 100000'})
    )
    cotizacion = forms.DecimalField(
        max_digits=8,
        decimal_places=2,
        required=False,
        label='Cotización del USD',
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Ej: 950'})
    )
    metodo = forms.ChoiceField(
        choices=[('pesos', 'Pesos Argentinos'), ('usd', 'Dólares'), ('mixto', 'Mixto')],
        required=False,
        label='Moneda de pago',
        widget=forms.Select(attrs={'class': 'form-control'})
    )


class SaleCardDetailForm(forms.Form):
    tarjeta = forms.CharField(
        max_length=50,
        required=False,
        label='Tarjeta utilizada',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Visa, Mastercard'})
    )
    monto_pesos = forms.DecimalField(
        max_digits=12,
        decimal_places=2,
        required=False,
        label='Monto total en pesos',
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Ej: 100000'})
    )
    cuotas = forms.IntegerField(
        required=False,
        label='Cantidad de cuotas',
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Ej: 3'})
    )
