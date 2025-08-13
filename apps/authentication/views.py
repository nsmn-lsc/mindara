"""
Vistas de la API de autenticación
Endpoints REST para React frontend
"""

from rest_framework import status, generics, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

from .models import User, UserProfile
from .serializers import (
    UserSerializer, UserRegistrationSerializer, UserLoginSerializer,
    PasswordChangeSerializer, UserLevelUpdateSerializer, UserProfileSerializer
)
from .permissions import IsAdminOrReadOnly, IsOwnerOrAdmin


class CustomTokenObtainPairView(TokenObtainPairView):
    """
    Vista personalizada para obtener tokens JWT
    Retorna información adicional del usuario junto con los tokens
    """
    
    def post(self, request, *args, **kwargs):
        serializer = UserLoginSerializer(data=request.data, context={'request': request})
        
        if serializer.is_valid():
            user = serializer.validated_data['user']
            
            # Generar tokens JWT
            refresh = RefreshToken.for_user(user)
            access_token = refresh.access_token
            
            # Serializar datos del usuario
            user_serializer = UserSerializer(user, context={'request': request})
            
            return Response({
                'tokens': {
                    'access': str(access_token),
                    'refresh': str(refresh),
                },
                'user': user_serializer.data,
                'message': 'Login exitoso'
            }, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserRegistrationView(APIView):
    """
    Vista para registro de nuevos usuarios
    Endpoint: POST /api/auth/register/
    """
    
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        """
        Registrar un nuevo usuario
        """
        serializer = UserRegistrationSerializer(data=request.data)
        
        if serializer.is_valid():
            user = serializer.save()
            
            # Generar tokens automáticamente tras el registro
            refresh = RefreshToken.for_user(user)
            access_token = refresh.access_token
            
            # Retornar datos del usuario y tokens
            user_data = UserSerializer(user, context={'request': request}).data
            
            return Response({
                'user': user_data,
                'tokens': {
                    'access': str(access_token),
                    'refresh': str(refresh),
                },
                'message': 'Usuario registrado exitosamente'
            }, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserProfileView(generics.RetrieveUpdateAPIView):
    """
    Vista para obtener y actualizar el perfil del usuario autenticado
    Endpoint: GET/PUT /api/auth/profile/
    """
    
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        """
        Retorna el usuario autenticado
        """
        return self.request.user
    
    def update(self, request, *args, **kwargs):
        """
        Actualizar perfil del usuario
        """
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        
        if serializer.is_valid():
            serializer.save()
            return Response({
                'user': serializer.data,
                'message': 'Perfil actualizado exitosamente'
            })
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PasswordChangeView(APIView):
    """
    Vista para cambio de contraseña
    Endpoint: POST /api/auth/change-password/
    """
    
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        """
        Cambiar contraseña del usuario autenticado
        """
        serializer = PasswordChangeSerializer(
            data=request.data, 
            context={'request': request}
        )
        
        if serializer.is_valid():
            serializer.save()
            return Response({
                'message': 'Contraseña cambiada exitosamente'
            }, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserListView(generics.ListAPIView):
    """
    Vista para listar usuarios (solo para admins y managers)
    Endpoint: GET /api/auth/users/
    """
    
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """
        Filtrar usuarios según el nivel del usuario autenticado
        """
        user = self.request.user
        
        if user.is_admin():
            # Los admins pueden ver todos los usuarios
            return User.objects.all()
        elif user.is_manager():
            # Los managers solo pueden ver usuarios básicos
            return User.objects.filter(user_level='USER')
        else:
            # Los usuarios básicos no pueden ver otros usuarios
            return User.objects.none()


class UserDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Vista para obtener, actualizar o eliminar un usuario específico
    Endpoint: GET/PUT/DELETE /api/auth/users/{id}/
    """
    
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrAdmin]
    
    def get_queryset(self):
        """
        Los usuarios solo pueden ver/editar su propio perfil
        Los admins pueden ver/editar cualquier usuario
        """
        user = self.request.user
        
        if user.is_admin():
            return User.objects.all()
        else:
            return User.objects.filter(id=user.id)


class UserLevelUpdateView(APIView):
    """
    Vista para que admins actualicen el nivel de otros usuarios
    Endpoint: PATCH /api/auth/users/{id}/level/
    """
    
    permission_classes = [permissions.IsAuthenticated]
    
    def patch(self, request, pk):
        """
        Actualizar nivel de usuario (solo admins)
        """
        if not request.user.is_admin():
            return Response({
                'error': 'No tienes permisos para realizar esta acción'
            }, status=status.HTTP_403_FORBIDDEN)
        
        try:
            user = User.objects.get(pk=pk)
        except User.DoesNotExist:
            return Response({
                'error': 'Usuario no encontrado'
            }, status=status.HTTP_404_NOT_FOUND)
        
        serializer = UserLevelUpdateSerializer(
            user, 
            data=request.data, 
            context={'request': request}
        )
        
        if serializer.is_valid():
            serializer.save()
            return Response({
                'user': UserSerializer(user, context={'request': request}).data,
                'message': 'Nivel de usuario actualizado'
            })
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def logout_view(request):
    """
    Vista para cerrar sesión
    Endpoint: POST /api/auth/logout/
    """
    try:
        # Blacklist del refresh token si se proporciona
        refresh_token = request.data.get('refresh_token')
        if refresh_token:
            token = RefreshToken(refresh_token)
            token.blacklist()
        
        logout(request)
        return Response({
            'message': 'Sesión cerrada exitosamente'
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'error': 'Error al cerrar sesión'
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def user_stats_view(request):
    """
    Vista para obtener estadísticas de usuarios (solo admins)
    Endpoint: GET /api/auth/stats/
    """
    if not request.user.is_admin():
        return Response({
            'error': 'No tienes permisos para ver estas estadísticas'
        }, status=status.HTTP_403_FORBIDDEN)
    
    stats = {
        'total_users': User.objects.count(),
        'active_users': User.objects.filter(is_active=True).count(),
        'inactive_users': User.objects.filter(is_active=False).count(),
        'admins': User.objects.filter(user_level='ADMIN').count(),
        'managers': User.objects.filter(user_level='MANAGER').count(),
        'basic_users': User.objects.filter(user_level='USER').count(),
    }
    
    return Response(stats, status=status.HTTP_200_OK)
