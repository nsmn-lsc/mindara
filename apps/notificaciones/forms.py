"""
Formularios para el módulo de notificaciones
"""

from django import forms
from django.utils import timezone
from datetime import timedelta
from .models import Notificacion
from apps.authentication.models import User


class NotificacionForm(forms.ModelForm):
    """Formulario para crear y editar notificaciones"""
    
    class Meta:
        model = Notificacion
        fields = [
            'titulo', 'mensaje', 'tipo', 'prioridad',
            'usuarios_objetivo', 'nivel_usuario_objetivo',
            'fecha_expiracion'
        ]
        
        widgets = {
            'titulo': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Título de la notificación'
            }),
            'mensaje': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Mensaje de la notificación'
            }),
            'tipo': forms.Select(attrs={
                'class': 'form-select'
            }),
            'prioridad': forms.Select(attrs={
                'class': 'form-select'
            }),
            'usuarios_objetivo': forms.SelectMultiple(attrs={
                'class': 'form-select',
                'size': '5'
            }),
            'nivel_usuario_objetivo': forms.Select(attrs={
                'class': 'form-select'
            }),
            'fecha_expiracion': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Personalizar queryset para usuarios
        self.fields['usuarios_objetivo'].queryset = User.objects.filter(
            is_active=True
        ).order_by('user_level', 'first_name', 'username')
        
        # Hacer que los campos no sean requeridos
        self.fields['usuarios_objetivo'].required = False
        self.fields['nivel_usuario_objetivo'].required = False
        self.fields['fecha_expiracion'].required = False
        
        # Personalizar labels
        self.fields['usuarios_objetivo'].label = 'Usuarios específicos'
        self.fields['nivel_usuario_objetivo'].label = 'Nivel de usuario objetivo'
        self.fields['fecha_expiracion'].label = 'Fecha de expiración'
        
        # Agregar help text
        self.fields['usuarios_objetivo'].help_text = 'Selecciona usuarios específicos (opcional)'
        self.fields['nivel_usuario_objetivo'].help_text = 'Selecciona un nivel de usuario (opcional)'
        self.fields['fecha_expiracion'].help_text = 'Fecha después de la cual la notificación no será visible'
    
    def clean(self):
        cleaned_data = super().clean()
        usuarios_objetivo = cleaned_data.get('usuarios_objetivo')
        nivel_usuario_objetivo = cleaned_data.get('nivel_usuario_objetivo')
        
        # Si se especifican usuarios específicos y nivel de usuario, dar prioridad a usuarios específicos
        if usuarios_objetivo and nivel_usuario_objetivo:
            cleaned_data['nivel_usuario_objetivo'] = None
        
        return cleaned_data


class NotificacionRapidaForm(forms.ModelForm):
    """Formulario simplificado para crear notificaciones rápidas"""
    
    class Meta:
        model = Notificacion
        fields = [
            'titulo', 'mensaje', 'prioridad', 'nivel_usuario_objetivo'
        ]
        
        widgets = {
            'titulo': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Título de la notificación'
            }),
            'mensaje': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Mensaje de la notificación'
            }),
            'prioridad': forms.Select(attrs={
                'class': 'form-select'
            }),
            'nivel_usuario_objetivo': forms.Select(attrs={
                'class': 'form-select'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Configurar el tipo como general para notificaciones rápidas
        self.tipo = 'general'
        
        # Hacer campos opcionales
        self.fields['nivel_usuario_objetivo'].required = False
        
        # Personalizar labels
        self.fields['nivel_usuario_objetivo'].label = 'Dirigida a'
        
        # Agregar help text
        self.fields['nivel_usuario_objetivo'].help_text = 'Deja vacío para enviar a todos'
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.tipo = 'general'  # Forzar tipo general para notificaciones rápidas
        
        if commit:
            instance.save()
        
        return instance
