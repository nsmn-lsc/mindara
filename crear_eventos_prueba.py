#!/usr/bin/env python
"""
Script para crear eventos de prueba en el sistema
"""
import os
import sys
import django
from datetime import datetime, timedelta

# Configurar Django
if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
    django.setup()
    
    from apps.eventos.models import Evento
    from apps.authentication.models import User
    from django.utils import timezone
    
    # Obtener usuarios
    try:
        admin_user = User.objects.get(email='admin@mindara.com')
        manager_user = User.objects.get(email='manager@mindara.com')
        user_user = User.objects.get(email='usuario@mindara.com')
    except User.DoesNotExist:
        print("Error: No se encontraron los usuarios necesarios")
        print("Asegúrate de haber ejecutado el script de inicialización de usuarios")
        sys.exit(1)
    
    print("Creando eventos de prueba...")
    
    # Eventos de prueba
    eventos_prueba = [
        {
            'nombre_evento': 'Reunión Semanal de Equipo',
            'objetivo': 'Reunión semanal para revisar el progreso del proyecto y planificar las siguientes tareas.',
            'fecha_evento': (timezone.now() + timedelta(days=1)).date(),
            'hora_evento': '10:00',
            'duracion': '1',
            'sede': 'Sala de Juntas A',
            'etapa': 'confirmado',
            'prioridad': 'media',
            'aforo': 8,
            'usuario': admin_user
        },
        {
            'nombre_evento': 'Cumpleaños de María',
            'objetivo': 'Celebración del cumpleaños de María en la oficina',
            'fecha_evento': (timezone.now() + timedelta(days=3)).date(),
            'hora_evento': '15:00',
            'duracion': '2',
            'sede': 'Área de descanso',
            'etapa': 'planificacion',
            'prioridad': 'baja',
            'aforo': 15,
            'usuario': manager_user
        },
        {
            'nombre_evento': 'Entrega de Reporte Mensual',
            'objetivo': 'Deadline para la entrega del reporte mensual de actividades',
            'fecha_evento': (timezone.now() + timedelta(days=7)).date(),
            'hora_evento': '17:00',
            'duracion': '1',
            'sede': 'Oficina',
            'etapa': 'planificacion',
            'prioridad': 'alta',
            'aforo': 5,
            'usuario': user_user
        },
        {
            'nombre_evento': 'Cita Médica Anual',
            'objetivo': 'Chequeo médico anual de rutina',
            'fecha_evento': (timezone.now() + timedelta(days=10)).date(),
            'hora_evento': '09:00',
            'duracion': '1',
            'sede': 'Clínica San José',
            'etapa': 'confirmado',
            'prioridad': 'media',
            'aforo': 1,
            'usuario': user_user
        },
        {
            'nombre_evento': 'Curso de Django Avanzado',
            'objetivo': 'Curso online sobre técnicas avanzadas de desarrollo con Django',
            'fecha_evento': (timezone.now() + timedelta(days=5)).date(),
            'hora_evento': '19:00',
            'duracion': '2',
            'sede': 'Virtual - https://meet.google.com/abc-defg-hij',
            'etapa': 'confirmado',
            'prioridad': 'media',
            'aforo': 20,
            'usuario': admin_user
        },
        {
            'nombre_evento': 'Viaje a Barcelona',
            'objetivo': 'Viaje de vacaciones familiares a Barcelona',
            'fecha_evento': (timezone.now() + timedelta(days=30)).date(),
            'hora_evento': '08:00',
            'duracion': '8',
            'sede': 'Barcelona, España',
            'etapa': 'planificacion',
            'prioridad': 'media',
            'aforo': 4,
            'usuario': manager_user
        }
    ]
    
    eventos_creados = 0
    for evento_data in eventos_prueba:
        # Verificar si ya existe un evento similar
        existe = Evento.objects.filter(
            nombre_evento=evento_data['nombre_evento'],
            usuario=evento_data['usuario']
        ).exists()
        
        if not existe:
            evento = Evento.objects.create(**evento_data)
            eventos_creados += 1
            print(f"✓ Evento creado: {evento.nombre_evento} - {evento.usuario.username}")
        else:
            print(f"• Evento ya existe: {evento_data['nombre_evento']}")
    
    print(f"\nTotal de eventos creados: {eventos_creados}")
    print(f"Total de eventos en el sistema: {Evento.objects.count()}")
    print("Datos de prueba creados exitosamente.")
