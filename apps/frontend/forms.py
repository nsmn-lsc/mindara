"""
Formularios para la gestión de usuarios por administradores
"""

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from apps.authentication.models import User


class AdminUserCreateForm(UserCreationForm):
    """
    Formulario para que los administradores creen nuevos usuarios
    """
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'correo@ejemplo.com'
        })
    )
    
    first_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nombre'
        })
    )
    
    last_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Apellido'
        })
    )
    
    user_level = forms.ChoiceField(
        choices=User.USER_LEVELS,
        initial='USER',
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )
    
    is_active = forms.BooleanField(
        required=False,
        initial=True,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        })
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'user_level', 'is_active', 'password1', 'password2')
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre de usuario'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Personalizar los campos de contraseña
        self.fields['password1'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Contraseña'
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Confirmar contraseña'
        })

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError('Ya existe un usuario con este email.')
        return email

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise ValidationError('Ya existe un usuario con este nombre de usuario.')
        return username

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.user_level = self.cleaned_data['user_level']
        user.is_active = self.cleaned_data['is_active']
        
        if commit:
            user.save()
        return user


class AdminUserEditForm(forms.ModelForm):
    """
    Formulario para editar usuarios (sin contraseña)
    """
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control'
        })
    )
    
    first_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control'
        })
    )
    
    last_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control'
        })
    )
    
    user_level = forms.ChoiceField(
        choices=User.USER_LEVELS,
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )
    
    is_active = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        })
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'user_level', 'is_active')
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'readonly': True  # El username no se puede cambiar
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # El username es solo lectura
        self.fields['username'].disabled = True

    def clean_email(self):
        email = self.cleaned_data.get('email')
        # Permitir el mismo email si es el usuario actual
        if self.instance and self.instance.email == email:
            return email
        if User.objects.filter(email=email).exists():
            raise ValidationError('Ya existe un usuario con este email.')
        return email


class UserSearchForm(forms.Form):
    """
    Formulario para buscar usuarios
    """
    search = forms.CharField(
        max_length=255,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Buscar por nombre, email o username...'
        })
    )
    
    user_level = forms.ChoiceField(
        choices=[('', 'Todos los niveles')] + User.USER_LEVELS,
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )
    
    is_active = forms.ChoiceField(
        choices=[
            ('', 'Todos los estados'),
            ('true', 'Activos'),
            ('false', 'Inactivos')
        ],
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )
