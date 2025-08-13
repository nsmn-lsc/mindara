"""
Permisos personalizados para la aplicación de autenticación
Define quién puede hacer qué según el nivel de usuario
"""

from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin
from rest_framework import permissions


class AdminManagerPermissionMixin(LoginRequiredMixin, UserPassesTestMixin):
    """
    Mixin que permite acceso solo a administradores y managers
    """
    
    def test_func(self):
        """
        Verificar que el usuario sea admin o manager
        """
        return (
            self.request.user.is_authenticated and 
            self.request.user.can_manage_users()
        )


class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Permiso personalizado que permite:
    - Solo administradores pueden escribir (POST, PUT, PATCH, DELETE)
    - Cualquier usuario autenticado puede leer (GET)
    """
    
    def has_permission(self, request, view):
        """
        Verificar permisos a nivel de vista
        """
        # Permitir lectura a usuarios autenticados
        if request.method in permissions.SAFE_METHODS:
            return request.user and request.user.is_authenticated
        
        # Solo admins pueden escribir
        return request.user and request.user.is_authenticated and request.user.is_admin()


class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Permiso personalizado que permite:
    - El propietario del objeto puede leer/escribir
    - Los administradores pueden leer/escribir cualquier objeto
    """
    
    def has_permission(self, request, view):
        """
        Verificar que el usuario esté autenticado
        """
        return request.user and request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        """
        Verificar permisos a nivel de objeto
        """
        # Los administradores pueden hacer todo
        if request.user.is_admin():
            return True
        
        # El propietario puede acceder a su propio objeto
        if hasattr(obj, 'user'):
            return obj.user == request.user
        
        # Si el objeto es un User, verificar que sea el mismo usuario
        if hasattr(obj, 'id') and hasattr(request.user, 'id'):
            return obj.id == request.user.id
        
        return False


class IsManagerOrAdmin(permissions.BasePermission):
    """
    Permiso que solo permite acceso a Managers y Administradores
    """
    
    def has_permission(self, request, view):
        """
        Solo managers y admins pueden acceder
        """
        return (
            request.user and 
            request.user.is_authenticated and 
            request.user.can_manage_users()
        )


class IsAdminOnly(permissions.BasePermission):
    """
    Permiso que solo permite acceso a Administradores
    """
    
    def has_permission(self, request, view):
        """
        Solo administradores pueden acceder
        """
        return (
            request.user and 
            request.user.is_authenticated and 
            request.user.is_admin()
        )


class CanManageUsers(permissions.BasePermission):
    """
    Permiso para gestionar usuarios según el nivel:
    - ADMIN: puede gestionar todos los usuarios
    - MANAGER: puede gestionar solo usuarios básicos (USER)
    - USER: no puede gestionar otros usuarios
    """
    
    def has_permission(self, request, view):
        """
        Verificar que el usuario puede gestionar otros usuarios
        """
        return (
            request.user and 
            request.user.is_authenticated and 
            request.user.can_manage_users()
        )
    
    def has_object_permission(self, request, view, obj):
        """
        Verificar permisos específicos según el nivel del usuario
        """
        # Los administradores pueden gestionar cualquier usuario
        if request.user.is_admin():
            return True
        
        # Los managers solo pueden gestionar usuarios básicos
        if request.user.is_manager():
            return obj.user_level == 'USER'
        
        # Los usuarios básicos no pueden gestionar otros usuarios
        return False


class IsOwnerOrManagerOrAdmin(permissions.BasePermission):
    """
    Permiso híbrido que permite:
    - Al propietario acceder a su propio objeto
    - A managers y admins acceder según sus permisos
    """
    
    def has_permission(self, request, view):
        """
        Usuario debe estar autenticado
        """
        return request.user and request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        """
        Verificar permisos combinados
        """
        # El propietario siempre puede acceder a su objeto
        if hasattr(obj, 'user') and obj.user == request.user:
            return True
        
        if hasattr(obj, 'id') and obj.id == request.user.id:
            return True
        
        # Los administradores pueden acceder a todo
        if request.user.is_admin():
            return True
        
        # Los managers pueden acceder a usuarios básicos
        if request.user.is_manager() and hasattr(obj, 'user_level'):
            return obj.user_level == 'USER'
        
        return False
