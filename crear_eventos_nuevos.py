#!/usr/bin/env python
"""
Script para crear eventos de prueba con el nuevo modelo
"""

import os
import django
import sys

# Configurar Django
sys.path.append('/home/najera/Documentos/Projects/Mindara')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from apps.eventos.models import Evento, CategoriaEvento
from apps.authentication.models import User
from datetime import date, time, datetime, timedelta

def crear_eventos_prueba():
    """Crear eventos de prueba para el nuevo modelo"""
    
    print("🎯 Creando eventos de prueba con el nuevo modelo...")
    
    # Obtener o crear usuarios
    try:
        admin_user = User.objects.filter(user_level='ADMIN').first()
        if not admin_user:
            admin_user = User.objects.create_user(
                username='admin_eventos',
                email='admin@mindara.com',
                password='admin123',
                user_level='ADMIN',
                first_name='Admin',
                last_name='Eventos'
            )
            print(f"✅ Usuario admin creado: {admin_user.username}")
        
        # Crear algunos usuarios manager y user si no existen
        manager_user = User.objects.filter(user_level='MANAGER').first()
        if not manager_user:
            manager_user = User.objects.create_user(
                username='manager_eventos',
                email='manager@mindara.com',
                password='manager123',
                user_level='MANAGER',
                first_name='Manager',
                last_name='Eventos'
            )
            print(f"✅ Usuario manager creado: {manager_user.username}")
            
        user_basico = User.objects.filter(user_level='USER').first()
        if not user_basico:
            user_basico = User.objects.create_user(
                username='user_eventos',
                email='user@mindara.com',
                password='user123',
                user_level='USER',
                first_name='Usuario',
                last_name='Básico'
            )
            print(f"✅ Usuario básico creado: {user_basico.username}")
            
    except Exception as e:
        print(f"⚠️  Error al crear usuarios: {e}")
        return
    
    # Crear categorías de ejemplo
    categorias_data = [
        {'nombre': 'Reuniones Ejecutivas', 'color': '#E53E3E', 'descripcion': 'Reuniones de alto nivel'},
        {'nombre': 'Capacitación', 'color': '#3182CE', 'descripcion': 'Eventos de formación y capacitación'},
        {'nombre': 'Presentaciones', 'color': '#38A169', 'descripcion': 'Presentaciones y demos'},
        {'nombre': 'Workshops', 'color': '#D69E2E', 'descripcion': 'Talleres y workshops'},
    ]
    
    for cat_data in categorias_data:
        categoria, created = CategoriaEvento.objects.get_or_create(
            nombre=cat_data['nombre'],
            defaults={
                'color': cat_data['color'],
                'descripcion': cat_data['descripcion']
            }
        )
        if created:
            print(f"✅ Categoría creada: {categoria.nombre}")
    
    # Crear eventos de prueba
    eventos_data = [
        {
            'nombre_evento': 'Reunión Estratégica Q1 2025',
            'objetivo': 'Definir objetivos y estrategias para el primer trimestre del año',
            'fecha_evento': date(2025, 8, 15),
            'hora_evento': time(9, 0),
            'duracion': '4',
            'sede': 'Sala de Juntas Principal - Oficina Central',
            'aforo': 15,
            'participantes': '''Director General
Director de Operaciones
Director de Marketing
Director de Ventas
Gerente de Finanzas''',
            'usuario': admin_user,
            'etapa': 'planificacion',
            'prioridad': 'alta',
            'carpeta_ejecutiva': True,
            'carpeta_ejecutiva_liga': 'https://drive.google.com/file/d/1ejemplo_presentacion_estrategica',
            'link_maps': 'https://maps.google.com/?q=Oficina+Central+Mindara',
            'compromisos': 'Definir presupuestos por área, establecer KPIs trimestrales',
            'observaciones': 'Incluir coffee break. Preparar material impreso para todos los asistentes.'
        },
        {
            'nombre_evento': 'Capacitación en Nuevas Tecnologías',
            'objetivo': 'Capacitar al equipo técnico en las últimas tecnologías de desarrollo',
            'fecha_evento': date(2025, 8, 20),
            'hora_evento': time(14, 0),
            'duracion': '6',
            'sede': 'Auditorio de Capacitación - Planta Baja',
            'aforo': 25,
            'participantes': '''Equipo de Desarrollo
Equipo de QA
DevOps Engineers
Technical Leads''',
            'usuario': manager_user,
            'etapa': 'revision',
            'prioridad': 'media',
            'carpeta_ejecutiva': True,
            'carpeta_ejecutiva_liga': 'https://drive.google.com/file/d/1ejemplo_capacitacion_tech',
            'link_maps': 'https://maps.google.com/?q=Auditorio+Capacitacion+Mindara',
            'compromisos': 'Evaluar conocimientos post-capacitación, crear plan de implementación',
            'observaciones': 'Solicitar laptops para práctica. Coordinar con IT el setup técnico.'
        },
        {
            'nombre_evento': 'Demo de Producto para Cliente Premium',
            'objetivo': 'Presentar las nuevas funcionalidades del producto al cliente estratégico',
            'fecha_evento': date(2025, 8, 25),
            'hora_evento': time(11, 0),
            'duracion': '2',
            'sede': 'Sala de Presentaciones VIP',
            'aforo': 8,
            'participantes': '''Account Manager
Product Manager
Technical Lead
Sales Director''',
            'usuario': manager_user,
            'etapa': 'confirmado',
            'prioridad': 'urgente',
            'carpeta_ejecutiva': True,
            'carpeta_ejecutiva_liga': 'https://drive.google.com/file/d/1ejemplo_demo_producto',
            'link_maps': 'https://maps.google.com/?q=Sala+VIP+Mindara',
            'compromisos': 'Seguimiento post-demo, preparar propuesta comercial',
            'observaciones': 'Preparar demo environment. Verificar equipos AV. Cliente muy importante.'
        },
        {
            'nombre_evento': 'Workshop de Design Thinking',
            'objetivo': 'Desarrollar habilidades de pensamiento creativo en el equipo',
            'fecha_evento': date(2025, 9, 5),
            'hora_evento': time(9, 30),
            'duracion': '8',
            'sede': 'Espacio Colaborativo - Área Creativa',
            'aforo': 20,
            'participantes': '''Equipo de Diseño
Product Managers
Marketing Team
Innovation Team''',
            'usuario': user_basico,
            'etapa': 'planificacion',
            'prioridad': 'media',
            'carpeta_ejecutiva': False,
            'link_maps': 'https://maps.google.com/?q=Espacio+Colaborativo+Mindara',
            'compromisos': 'Aplicar metodologías aprendidas en proyectos actuales',
            'observaciones': 'Incluir material de papelería. Organizar lunch. Facilitador externo confirmado.'
        },
        {
            'nombre_evento': 'Reunión de Seguimiento de Proyectos',
            'objetivo': 'Revisar el avance de los proyectos en curso y resolver bloqueadores',
            'fecha_evento': date(2025, 8, 12),
            'hora_evento': time(16, 0),
            'duracion': '1.5',
            'sede': 'Sala de Reuniones 3',
            'aforo': 12,
            'participantes': '''Project Managers
Team Leads
Stakeholders clave''',
            'usuario': admin_user,
            'etapa': 'confirmado',
            'prioridad': 'alta',
            'carpeta_ejecutiva': False,
            'link_maps': 'https://maps.google.com/?q=Sala+Reuniones+3+Mindara',
            'compromisos': 'Actualizar cronogramas, resolver issues críticos',
            'observaciones': 'Reunión semanal. Preparar reportes de avance.'
        }
    ]
    
    # Crear los eventos
    eventos_creados = 0
    for evento_data in eventos_data:
        try:
            evento = Evento.objects.create(**evento_data)
            eventos_creados += 1
            print(f"✅ Evento creado: {evento.nombre_evento} ({evento.fecha_evento})")
        except Exception as e:
            print(f"❌ Error al crear evento '{evento_data['nombre_evento']}': {e}")
    
    print(f"\n🎉 Proceso completado!")
    print(f"📊 Estadísticas:")
    print(f"   • Eventos creados: {eventos_creados}")
    print(f"   • Total de eventos: {Evento.objects.count()}")
    print(f"   • Total de categorías: {CategoriaEvento.objects.count()}")
    print(f"   • Total de usuarios: {User.objects.count()}")

if __name__ == '__main__':
    crear_eventos_prueba()
