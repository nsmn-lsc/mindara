#!/usr/bin/env python
"""
Script para crear una notificación de prueba
"""

import os
import sys
import django

# Configurar el entorno de Django
sys.path.append('/home/najera/Documentos/Projects/Mindara')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.contrib.auth import get_user_model
from apps.notificaciones.models import Notificacion
from django.utils import timezone
from datetime import timedelta

User = get_user_model()

def crear_notificacion_prueba():
    """Crear una notificación de prueba"""
    
    # Obtener el primer usuario admin/manager
    admin_user = User.objects.filter(user_level__in=['ADMIN', 'MANAGER']).first()
    
    if not admin_user:
        print("❌ No se encontró un usuario admin o manager")
        return
    
    # Crear la notificación
    notificacion = Notificacion.objects.create(
        titulo="🎉 ¡Bienvenido al Sistema de Notificaciones!",
        mensaje="Esta es una notificación de prueba para demostrar el nuevo sistema de notificaciones de Mindara. El sistema permite enviar mensajes a usuarios específicos o por niveles de usuario, con diferentes prioridades y fechas de expiración.",
        tipo="sistema",
        prioridad="alta",
        creado_por=admin_user,
        fecha_expiracion=timezone.now() + timedelta(days=7),  # Expira en 7 días
        activa=True
    )
    
    print(f"✅ Notificación creada exitosamente:")
    print(f"   ID: {notificacion.id}")
    print(f"   Título: {notificacion.titulo}")
    print(f"   Creada por: {notificacion.creado_por.username}")
    print(f"   Fecha: {notificacion.fecha_creacion}")
    print(f"   Activa: {notificacion.activa}")
    
    # Crear otra notificación para usuarios específicos
    notificacion2 = Notificacion.objects.create(
        titulo="📅 Recordatorio de Eventos",
        mensaje="No olvides revisar tu calendario de eventos. Hay nuevas funcionalidades disponibles en el módulo de eventos.",
        tipo="evento",
        prioridad="media",
        creado_por=admin_user,
        nivel_usuario_objetivo="USER",  # Solo para usuarios básicos
        activa=True
    )
    
    print(f"✅ Segunda notificación creada:")
    print(f"   ID: {notificacion2.id}")
    print(f"   Título: {notificacion2.titulo}")
    print(f"   Dirigida a: {notificacion2.nivel_usuario_objetivo}")
    
    # Crear una notificación para managers
    notificacion3 = Notificacion.objects.create(
        titulo="⚙️ Panel de Administración",
        mensaje="Se han agregado nuevas funcionalidades al panel de administración. Revisa las nuevas opciones de gestión de notificaciones.",
        tipo="general",
        prioridad="baja",
        creado_por=admin_user,
        nivel_usuario_objetivo="MANAGER",  # Solo para managers
        activa=True
    )
    
    print(f"✅ Tercera notificación creada:")
    print(f"   ID: {notificacion3.id}")
    print(f"   Título: {notificacion3.titulo}")
    print(f"   Dirigida a: {notificacion3.nivel_usuario_objetivo}")
    
    print(f"\n🎯 Total de notificaciones creadas: 3")
    print(f"💡 Visita http://127.0.0.1:8000/notificaciones/mis-notificaciones/ para verlas")

if __name__ == "__main__":
    crear_notificacion_prueba()
