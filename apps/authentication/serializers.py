"""
Serializers para la API de autenticación
Convierte los modelos Django en JSON para React
"""

from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from .models import User, UserProfile


class UserProfileSerializer(serializers.ModelSerializer):
    """
    Serializer para el perfil del usuario
    Maneja la información extendida del usuario
    """
    
    class Meta:
        model = UserProfile
        fields = [
            'bio', 'location', 'website', 'birth_date',
            'privacy_email', 'privacy_phone',
            'notifications_email', 'notifications_push'
        ]


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer principal para el modelo User
    Incluye validaciones de seguridad y métodos helper
    """
    
    profile = UserProfileSerializer(read_only=True)
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True)
    full_name = serializers.SerializerMethodField()
    avatar_url = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'user_level', 'phone', 'avatar', 'avatar_url', 'is_active',
            'date_joined', 'last_login', 'created_at', 'updated_at',
            'password', 'password_confirm', 'full_name', 'profile'
        ]
        read_only_fields = ['id', 'date_joined', 'last_login', 'created_at', 'updated_at']
    
    def get_full_name(self, obj):
        """Retorna el nombre completo del usuario"""
        return obj.get_full_name()
    
    def get_avatar_url(self, obj):
        """Retorna la URL completa del avatar"""
        if obj.avatar and hasattr(obj.avatar, 'url'):
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.avatar.url)
            return obj.avatar.url
        return None
    
    def validate(self, attrs):
        """
        Validación personalizada para el registro de usuarios
        """
        # Validar que las contraseñas coincidan
        if attrs.get('password') != attrs.get('password_confirm'):
            raise serializers.ValidationError({
                'password_confirm': 'Las contraseñas no coinciden.'
            })
        
        # Validar fortaleza de la contraseña
        password = attrs.get('password')
        if password:
            try:
                validate_password(password)
            except ValidationError as e:
                raise serializers.ValidationError({
                    'password': list(e.messages)
                })
        
        # Eliminar password_confirm antes de crear el usuario
        attrs.pop('password_confirm', None)
        return attrs
    
    def create(self, validated_data):
        """
        Crear un nuevo usuario con contraseña encriptada
        """
        password = validated_data.pop('password')
        user = User.objects.create_user(**validated_data)
        user.set_password(password)
        user.save()
        
        # Crear perfil automáticamente
        UserProfile.objects.create(user=user)
        
        return user
    
    def update(self, instance, validated_data):
        """
        Actualizar usuario existente
        """
        password = validated_data.pop('password', None)
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        if password:
            instance.set_password(password)
        
        instance.save()
        return instance


class UserRegistrationSerializer(UserSerializer):
    """
    Serializer específico para el registro de usuarios
    Solo permite crear usuarios con nivel 'USER' por defecto
    """
    
    class Meta(UserSerializer.Meta):
        fields = [
            'username', 'email', 'first_name', 'last_name',
            'phone', 'password', 'password_confirm'
        ]
    
    def create(self, validated_data):
        """
        Los nuevos usuarios siempre se crean con nivel 'USER'
        """
        validated_data['user_level'] = 'USER'
        return super().create(validated_data)


class UserLoginSerializer(serializers.Serializer):
    """
    Serializer para el login de usuarios
    Acepta email y contraseña
    """
    
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    
    def validate(self, attrs):
        """
        Validar credenciales de usuario
        """
        email = attrs.get('email')
        password = attrs.get('password')
        
        if email and password:
            # Autenticar usuario por email
            try:
                user = User.objects.get(email=email)
                user = authenticate(
                    request=self.context.get('request'),
                    username=user.username,
                    password=password
                )
                
                if not user:
                    raise serializers.ValidationError(
                        'Credenciales inválidas. Verifica tu email y contraseña.'
                    )
                
                if not user.is_active:
                    raise serializers.ValidationError(
                        'Esta cuenta está desactivada.'
                    )
                
                attrs['user'] = user
                return attrs
                
            except User.DoesNotExist:
                raise serializers.ValidationError(
                    'No existe un usuario con este email.'
                )
        else:
            raise serializers.ValidationError(
                'Email y contraseña son requeridos.'
            )


class PasswordChangeSerializer(serializers.Serializer):
    """
    Serializer para cambio de contraseña
    """
    
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True, min_length=8)
    new_password_confirm = serializers.CharField(write_only=True)
    
    def validate_old_password(self, value):
        """
        Validar que la contraseña actual sea correcta
        """
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError('Contraseña actual incorrecta.')
        return value
    
    def validate(self, attrs):
        """
        Validar que las nuevas contraseñas coincidan
        """
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError({
                'new_password_confirm': 'Las nuevas contraseñas no coinciden.'
            })
        
        # Validar fortaleza de la nueva contraseña
        try:
            validate_password(attrs['new_password'])
        except ValidationError as e:
            raise serializers.ValidationError({
                'new_password': list(e.messages)
            })
        
        return attrs
    
    def save(self):
        """
        Cambiar la contraseña del usuario
        """
        user = self.context['request'].user
        user.set_password(self.validated_data['new_password'])
        user.save()
        return user


class UserLevelUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer para que administradores actualicen el nivel de otros usuarios
    Solo disponible para usuarios ADMIN
    """
    
    class Meta:
        model = User
        fields = ['user_level']
    
    def validate_user_level(self, value):
        """
        Solo administradores pueden cambiar niveles de usuario
        """
        request_user = self.context['request'].user
        if not request_user.is_admin():
            raise serializers.ValidationError(
                'No tienes permisos para cambiar niveles de usuario.'
            )
        return value
