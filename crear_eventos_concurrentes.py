#!/usr/bin/env python
"""
Script para crear eventos de prueba con fechas y horas concurrentes
para probar el sistema de manejo de eventos superpuestos
"""

import os
import sys
import django
from datetime import datetime, date, time

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from apps.eventos.models import Evento, CategoriaEvento
from apps.authentication.models import User


def crear_eventos_concurrentes():
    """
    Crear eventos de prueba con fechas y horas superpuestas
    """
    print("🎯 Creando eventos de prueba concurrentes...")
    
    # Obtener o crear usuario para los eventos
    try:
        user = User.objects.filter(is_active=True).first()
        if not user:
            print("❌ No hay usuarios activos en el sistema")
            return
        
        print(f"📋 Usuario encontrado: {user.username} ({user.get_user_level_display()})")
        
        # Obtener o crear categoría (si existe en el modelo)
        # categoria, created = CategoriaEvento.objects.get_or_create(
        #     nombre='Reuniones',
        #     defaults={
        #         'descripcion': 'Reuniones de trabajo y coordinación',
        #         'color': '#06A77D'
        #     }
        # )
        
        # if created:
        #     print(f"✅ Categoría creada: {categoria.nombre}")
        # else:
        #     print(f"📁 Categoría existente: {categoria.nombre}")
        
        # Fecha de prueba (mañana)
        fecha_prueba = date(2025, 8, 8)  # 8 de agosto de 2025
        hora_base = time(10, 0)  # 10:00 AM
        
        # Lista de eventos concurrentes
        eventos_data = [
            {
                'nombre_evento': 'Reunión de Planificación Semanal',
                'objetivo': 'Revisar objetivos y metas de la semana',
                'fecha_evento': fecha_prueba,
                'hora_evento': hora_base,
                'duracion': '2',
                'sede': 'Sala de Conferencias A',
                'prioridad': 'alta',
                'etapa': 'confirmado',
                'aforo': 8,
                'participantes': 'Ana García\nCarlos Mendez\nLuisa Torres\nMiguel Ruiz',
                'observaciones': 'Reunión semanal para coordinar actividades y revisar avances del proyecto.',
            },
            {
                'nombre_evento': 'Sesión de Capacitación Técnica',
                'objetivo': 'Capacitar al equipo en nuevas tecnologías',
                'fecha_evento': fecha_prueba,
                'hora_evento': hora_base,  # Misma hora - CONFLICTO
                'duracion': '3',
                'sede': 'Laboratorio de Cómputo',
                'prioridad': 'media',
                'etapa': 'confirmado',
                'aforo': 12,
                'participantes': 'Carlos Rodríguez\nJuan Pérez\nMaría González\nLuis Martínez',
                'observaciones': 'Capacitación sobre las últimas actualizaciones de framework y herramientas.',
            },
            {
                'nombre_evento': 'Entrevista con Cliente VIP',
                'objetivo': 'Presentar propuesta comercial',
                'fecha_evento': fecha_prueba,
                'hora_evento': hora_base,  # Misma hora - CONFLICTO
                'duracion': '1.5',
                'sede': 'Oficina Principal - Sala Ejecutiva',
                'prioridad': 'urgente',
                'etapa': 'confirmado',
                'aforo': 4,
                'participantes': 'María Fernández\nRoberto Silva\nCliente VIP\nAsistente',
                'observaciones': 'Reunión crucial con cliente potencial de alto valor.',
                'carpeta_ejecutiva': True,
                'carpeta_ejecutiva_liga': 'https://drive.google.com/presentation/d/ejemplo',
            },
            {
                'nombre_evento': 'Review de Código y Arquitectura',
                'objetivo': 'Revisar calidad del código del sprint',
                'fecha_evento': fecha_prueba,
                'hora_evento': time(10, 30),  # 30 min después - CONFLICTO PARCIAL
                'duracion': '2',
                'sede': 'Sala de Reuniones B',
                'prioridad': 'alta',
                'etapa': 'confirmado',
                'aforo': 6,
                'participantes': 'Luis Martinez\nCarlos Tech\nAna Dev\nMiguel Code',
                'observaciones': 'Sesión de review técnico para asegurar calidad del código.',
            },
            {
                'nombre_evento': 'Presentación Trimestral de Resultados',
                'objetivo': 'Mostrar métricas y logros del trimestre',
                'fecha_evento': fecha_prueba,
                'hora_evento': time(11, 0),  # 1 hora después - CONFLICTO PARCIAL
                'duracion': '4',
                'sede': 'Auditorio Principal',
                'prioridad': 'urgente',
                'etapa': 'confirmado',
                'aforo': 25,
                'participantes': 'Todo el equipo directivo\nJefes de departamento\nCoordinadores\nInvitados especiales',
                'observaciones': 'Presentación ejecutiva de resultados trimestrales a todos los stakeholders.',
                'carpeta_ejecutiva': True,
                'carpeta_ejecutiva_liga': 'https://drive.google.com/presentation/d/resultados-q3',
            }
        ]
        
        eventos_creados = []
        
        for evento_data in eventos_data:
            evento, created = Evento.objects.get_or_create(
                nombre_evento=evento_data['nombre_evento'],
                fecha_evento=evento_data['fecha_evento'],
                defaults={
                    **evento_data,
                    'usuario': user,
                }
            )
            
            if created:
                eventos_creados.append(evento)
                print(f"✅ Evento creado: {evento.nombre_evento} - {evento.hora_evento}")
            else:
                print(f"⚠️  Evento ya existe: {evento.nombre_evento}")
        
        print(f"\n🎉 Resumen de eventos concurrentes creados:")
        print(f"📅 Fecha: {fecha_prueba.strftime('%A, %d de %B de %Y')}")
        print(f"🕐 Hora base: {hora_base.strftime('%H:%M')}")
        print(f"📊 Total de eventos: {len(eventos_creados)}")
        
        if eventos_creados:
            print(f"\n📋 Eventos creados por hora:")
            for evento in sorted(eventos_creados, key=lambda x: x.hora_evento):
                duracion_text = dict(Evento.DURACION_CHOICES).get(evento.duracion, evento.duracion)
                prioridad_text = dict(Evento.PRIORIDAD_CHOICES).get(evento.prioridad, evento.prioridad)
                
                print(f"  🕐 {evento.hora_evento.strftime('%H:%M')} - {evento.nombre_evento}")
                print(f"     ⏱️  Duración: {duracion_text}")
                print(f"     🔥 Prioridad: {prioridad_text}")
                print(f"     📍 Sede: {evento.sede}")
                print(f"     👥 Aforo: {evento.aforo}")
                print()
        
        # Verificar conflictos
        print("🔍 Análisis de conflictos de horario:")
        conflictos = detectar_conflictos(eventos_creados)
        
        if conflictos:
            print("⚠️  Se detectaron los siguientes conflictos:")
            for conflicto in conflictos:
                print(f"  🔴 {conflicto}")
        else:
            print("✅ No se detectaron conflictos de horario")
            
        print(f"\n🌐 Ahora puedes ir al calendario para ver cómo se manejan los eventos concurrentes")
        print(f"📱 URL: http://localhost:8000/eventos/")
        
    except Exception as e:
        print(f"❌ Error al crear eventos: {str(e)}")
        import traceback
        traceback.print_exc()


def detectar_conflictos(eventos):
    """
    Detectar conflictos de horario entre eventos
    """
    conflictos = []
    
    for i, evento1 in enumerate(eventos):
        for evento2 in eventos[i+1:]:
            if evento1.fecha_evento == evento2.fecha_evento:
                # Calcular tiempo de fin para cada evento
                duracion1 = float(evento1.duracion) if evento1.duracion != 'otro' else 2.0
                duracion2 = float(evento2.duracion) if evento2.duracion != 'otro' else 2.0
                
                inicio1 = datetime.combine(evento1.fecha_evento, evento1.hora_evento)
                fin1 = inicio1.replace(hour=inicio1.hour + int(duracion1), 
                                     minute=inicio1.minute + int((duracion1 % 1) * 60))
                
                inicio2 = datetime.combine(evento2.fecha_evento, evento2.hora_evento)
                fin2 = inicio2.replace(hour=inicio2.hour + int(duracion2), 
                                     minute=inicio2.minute + int((duracion2 % 1) * 60))
                
                # Verificar superposición
                if inicio1 < fin2 and inicio2 < fin1:
                    conflicto = f"{evento1.nombre_evento} ({evento1.hora_evento}) vs {evento2.nombre_evento} ({evento2.hora_evento})"
                    conflictos.append(conflicto)
    
    return conflictos


if __name__ == '__main__':
    crear_eventos_concurrentes()
