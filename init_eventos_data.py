#!/usr/bin/env python
"""
Script para inicializar datos de prueba de la aplicación eventos
"""
import os
import sys
import django

# Configurar Django
if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
    django.setup()
    
    from apps.eventos.models import CategoriaEvento
    from django.contrib.auth import get_user_model
    
    User = get_user_model()
    
    # Crear categorías de eventos
    categorias = [
        {
            'nombre': 'Reuniones',
            'descripcion': 'Reuniones de trabajo, juntas y conferencias',
            'color': '#3B82F6'  # Azul
        },
        {
            'nombre': 'Eventos Personales',
            'descripcion': 'Cumpleaños, aniversarios y eventos familiares',
            'color': '#10B981'  # Verde
        },
        {
            'nombre': 'Tareas Importantes',
            'descripcion': 'Deadlines, entregas y tareas prioritarias',
            'color': '#F59E0B'  # Amarillo
        },
        {
            'nombre': 'Salud y Bienestar',
            'descripcion': 'Citas médicas, ejercicio y actividades de bienestar',
            'color': '#EF4444'  # Rojo
        },
        {
            'nombre': 'Educación',
            'descripcion': 'Cursos, seminarios y actividades educativas',
            'color': '#8B5CF6'  # Púrpura
        },
        {
            'nombre': 'Viajes',
            'descripcion': 'Vacaciones, viajes de trabajo y desplazamientos',
            'color': '#06B6D4'  # Cian
        }
    ]
    
    print("Creando categorías de eventos...")
    
    for cat_data in categorias:
        categoria, created = CategoriaEvento.objects.get_or_create(
            nombre=cat_data['nombre'],
            defaults={
                'descripcion': cat_data['descripcion'],
                'color': cat_data['color'],
                'activa': True
            }
        )
        
        if created:
            print(f"✓ Categoría creada: {categoria.nombre}")
        else:
            print(f"• Categoría ya existe: {categoria.nombre}")
    
    print(f"\nTotal de categorías: {CategoriaEvento.objects.count()}")
    print("Inicialización completada.")
