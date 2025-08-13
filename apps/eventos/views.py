"""
Vistas para la aplicación de eventos
Sistema de gestión de eventos para usuarios de Mindara
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views.generic import View
from django.db.models import Q
from django.utils import timezone
from datetime import timedelta
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.core.paginator import Paginator
import json

from .models import Evento, CategoriaEvento
from apps.notificaciones.models import Notificacion, NotificacionLeida


@method_decorator(login_required, name='dispatch')
class EventosView(View):
    """
    Vista principal para el módulo de eventos
    """
    
    def get(self, request):
        """
        Mostrar la página principal de eventos
        """
        context = {
            'title': 'Eventos',
            'current_section': 'eventos'
        }
        return render(request, 'eventos/eventos.html', context)


@method_decorator(login_required, name='dispatch')
class PerfilView(View):
    """
    Vista para el perfil del usuario
    """
    
    def get(self, request):
        """
        Mostrar la página de perfil del usuario
        """
        user = request.user
        
        # Obtener notificaciones del usuario
        notificaciones_queryset = Notificacion.objects.get_for_user(user).order_by('-fecha_creacion')
        
        # Filtrar por fecha de expiración
        notificaciones_queryset = [
            n for n in notificaciones_queryset 
            if not n.fecha_expiracion or n.fecha_expiracion > timezone.now()
        ]
        
        # Tomar solo las últimas 10 para el perfil
        notificaciones_recientes = notificaciones_queryset[:10]
        
        # Marcar notificaciones como leídas cuando se ven
        for notificacion in notificaciones_recientes:
            NotificacionLeida.objects.get_or_create(
                notificacion=notificacion,
                usuario=user
            )
        
        context = {
            'title': 'Mi Perfil',
            'current_section': 'perfil',
            'user': user,
            'notificaciones_recientes': notificaciones_recientes,
            'total_notificaciones': len(notificaciones_queryset),
        }
        return render(request, 'eventos/perfil.html', context)
    
    def post(self, request):
        """
        Actualizar información del perfil del usuario (sin contraseña)
        """
        try:
            user = request.user
            
            # Actualizar información básica (sin contraseña ni username)
            if 'first_name' in request.POST:
                user.first_name = request.POST.get('first_name', '').strip()
            if 'last_name' in request.POST:
                user.last_name = request.POST.get('last_name', '').strip()
            if 'email' in request.POST:
                user.email = request.POST.get('email', '').strip()
            
            user.save()
            messages.success(request, 'Perfil actualizado correctamente.')
            
        except Exception as e:
            messages.error(request, f'Error al actualizar el perfil: {str(e)}')
        
        return redirect('eventos:perfil')


@login_required
def notificaciones_usuario(request):
    """Vista para ver todas las notificaciones del usuario"""
    user = request.user
    
    # Obtener todas las notificaciones del usuario
    notificaciones_queryset = Notificacion.objects.get_for_user(user).order_by('-fecha_creacion')
    
    # Filtrar por fecha de expiración
    notificaciones_list = [
        n for n in notificaciones_queryset 
        if not n.fecha_expiracion or n.fecha_expiracion > timezone.now()
    ]
    
    # Paginación
    paginator = Paginator(notificaciones_list, 20)
    page_number = request.GET.get('page')
    notificaciones = paginator.get_page(page_number)
    
    # Marcar como leídas las notificaciones de la página actual
    for notificacion in notificaciones:
        NotificacionLeida.objects.get_or_create(
            notificacion=notificacion,
            usuario=user
        )
    
    context = {
        'notificaciones': notificaciones,
        'total_notificaciones': len(notificaciones_list),
        'title': 'Mis Notificaciones',
        'current_section': 'notificaciones',
    }
    
    return render(request, 'eventos/notificaciones.html', context)


@login_required
def api_eventos_usuario(request):
    """
    API para obtener los eventos del usuario actual
    """
    if request.method == 'GET':
        try:
            user = request.user
            
            # Obtener eventos según el nivel del usuario
            if user.is_admin():
                # Los admins ven todos los eventos
                eventos = Evento.objects.all()
            elif user.is_manager():
                # Los managers ven todos los eventos
                eventos = Evento.objects.all()
            else:
                # Los usuarios básicos solo ven sus eventos
                eventos = Evento.objects.filter(usuario=user)
            
            # Serializar los eventos
            eventos_data = []
            for evento in eventos.order_by('-fecha_evento', '-hora_evento'):  # Todos los eventos para el calendario
                fecha_hora_inicio = evento.fecha_hora_completa
                fecha_hora_fin = fecha_hora_inicio + timedelta(hours=evento.duracion_real)
                
                eventos_data.append({
                    'id': evento.id,
                    'titulo': evento.nombre_evento,
                    'descripcion': evento.objetivo[:100] + '...' if len(evento.objetivo) > 100 else evento.objetivo,
                    'fecha_inicio': fecha_hora_inicio.isoformat(),  # Formato ISO para FullCalendar
                    'fecha_fin': fecha_hora_fin.isoformat(),
                    'estado': evento.etapa,
                    'estado_display': evento.get_etapa_display(),
                    'prioridad': evento.prioridad,
                    'prioridad_display': evento.get_prioridad_display(),
                    'categoria': None,  # Ya no usamos categorías
                    'categoria_color': '#06A77D',  # Color por defecto
                    'ubicacion': evento.sede,
                    'es_creador': evento.usuario == user,
                    'puede_editar': evento.puede_editar(user),
                    'duracion_horas': evento.duracion_real,
                    'esta_activo': evento.esta_en_progreso,
                    'ha_terminado': evento.ha_terminado,
                    'evidencias': evento.evidencias,
                    'usuario': {
                        'id': evento.usuario.id,
                        'nombre': f"{evento.usuario.first_name} {evento.usuario.last_name}".strip() or evento.usuario.username,
                        'username': evento.usuario.username,
                    }
                })
            
            return JsonResponse({
                'success': True,
                'eventos': eventos_data,
                'total': eventos.count()
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Error al obtener eventos: {str(e)}'
            }, status=500)
    
    return JsonResponse({
        'success': False,
        'message': 'Método no permitido'
    }, status=405)


@login_required
def api_perfil_stats(request):
    """
    API para obtener estadísticas del perfil del usuario
    """
    if request.method == 'GET':
        try:
            user = request.user
            
            # Obtener estadísticas de eventos del usuario
            total_eventos = Evento.objects.filter(
                usuario=user
            ).count()
            
            eventos_activos = Evento.objects.filter(
                usuario=user,
                etapa='confirmado',
                fecha_evento__gte=timezone.now().date()
            ).count()
            
            eventos_completados = Evento.objects.filter(
                usuario=user,
                etapa='confirmado',
                fecha_evento__lt=timezone.now().date()
            ).count()
            
            # Últimas actividades
            ultimas_actividades = []
            eventos_recientes = Evento.objects.filter(
                usuario=user
            ).order_by('-updated_at')[:5]
            
            for evento in eventos_recientes:
                ultimas_actividades.append({
                    'titulo': evento.nombre_evento,
                    'tipo': 'evento',
                    'fecha': evento.updated_at.strftime('%d/%m/%Y %H:%M'),
                    'estado': evento.get_etapa_display(),
                    'icono': 'fas fa-calendar-alt'
                })
            
            return JsonResponse({
                'success': True,
                'stats': {
                    'total_eventos': total_eventos,
                    'eventos_activos': eventos_activos,
                    'eventos_completados': eventos_completados,
                    'ultimas_actividades': ultimas_actividades
                }
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Error al obtener estadísticas: {str(e)}'
            }, status=500)
    
    return JsonResponse({
        'success': False,
        'message': 'Método no permitido'
    }, status=405)


@login_required
@csrf_exempt
def api_eventos(request):
    """
    API para gestionar eventos (GET, POST)
    """
    if request.method == 'GET':
        try:
            user = request.user
            
            # Obtener eventos según el nivel del usuario
            if user.is_admin() or user.is_manager():
                # Admins y managers ven todos los eventos
                eventos = Evento.objects.all()
            else:
                # Usuarios básicos solo ven sus eventos
                eventos = Evento.objects.filter(usuario=user)
            
            # Aplicar filtros si se proporcionan
            search = request.GET.get('search', '')
            status = request.GET.get('status', '')
            
            if search:
                eventos = eventos.filter(
                    Q(nombre_evento__icontains=search) |
                    Q(objetivo__icontains=search)
                )
            
            if status:
                # Mapear estados del frontend a etapas del modelo
                status_map = {
                    'activo': ['planificacion', 'revision', 'confirmado'],
                    'completado': ['confirmado'],
                    'cancelado': ['cancelado'],
                }
                if status in status_map:
                    eventos = eventos.filter(etapa__in=status_map[status])
            
            # Serializar los eventos
            eventos_data = []
            for evento in eventos.order_by('-fecha_evento', '-hora_evento'):
                eventos_data.append({
                    'id': evento.id,
                    'titulo': evento.nombre_evento,
                    'descripcion': evento.objetivo,
                    'fecha_inicio': evento.fecha_hora_completa.isoformat(),
                    'fecha_fin': (evento.fecha_hora_completa + timedelta(hours=evento.duracion_real)).isoformat(),
                    'ubicacion': evento.sede,
                    'prioridad': evento.prioridad,
                    'estado': evento.etapa,
                    'estado_display': evento.get_etapa_display(),
                    'categoria_nombre': 'Evento',  # Valor por defecto ya que no usamos categorías
                    'usuario': {
                        'id': evento.usuario.id,
                        'nombre': evento.usuario.get_full_name() or evento.usuario.username,
                        'email': evento.usuario.email,
                    },
                    'puede_editar': evento.puede_editar(user),
                    'puede_ver': evento.puede_ver(user),
                    'carpeta_ejecutiva': evento.carpeta_ejecutiva,
                    'carpeta_ejecutiva_liga': evento.carpeta_ejecutiva_liga if evento.carpeta_ejecutiva else None,
                    'ha_terminado': evento.ha_terminado,
                    'evidencias': evento.evidencias,
                    # Campos adicionales útiles
                    'aforo': evento.aforo,
                    'participantes': evento.participantes,
                    'observaciones': evento.observaciones,
                    'link_maps': evento.link_maps,
                })
            
            return JsonResponse({
                'success': True,
                'eventos': eventos_data,
                'total': len(eventos_data)
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Error al obtener eventos: {str(e)}'
            }, status=500)
    
    elif request.method == 'POST':
        try:
            user = request.user
            data = json.loads(request.body)
            
            # Validar campos requeridos
            nombre_evento = data.get('nombre_evento', '').strip()
            if not nombre_evento:
                return JsonResponse({
                    'success': False,
                    'message': 'El nombre del evento es requerido'
                }, status=400)
            
            fecha_evento = data.get('fecha_evento')
            if not fecha_evento:
                return JsonResponse({
                    'success': False,
                    'message': 'La fecha del evento es requerida'
                }, status=400)
            
            hora_evento = data.get('hora_evento')
            if not hora_evento:
                return JsonResponse({
                    'success': False,
                    'message': 'La hora del evento es requerida'
                }, status=400)
            
            # Parsear fecha y hora
            try:
                from datetime import datetime
                fecha_parsed = datetime.strptime(fecha_evento, '%Y-%m-%d').date()
                hora_parsed = datetime.strptime(hora_evento, '%H:%M').time()
            except ValueError:
                return JsonResponse({
                    'success': False,
                    'message': 'Formato de fecha u hora inválido'
                }, status=400)
            
            # Crear datos del evento
            evento_data = {
                'nombre_evento': nombre_evento,
                'objetivo': data.get('objetivo', 'Por definir'),
                'fecha_evento': fecha_parsed,
                'hora_evento': hora_parsed,
                'duracion': data.get('duracion', '2'),
                'sede': data.get('sede', 'Por definir'),
                'prioridad': data.get('prioridad', 'media'),
                'etapa': data.get('etapa', 'planificacion'),
                'aforo': int(data.get('aforo', 10)),
                'usuario': user,
                'link_maps': data.get('link_maps', ''),
                'participantes': data.get('participantes', ''),
                'carpeta_ejecutiva': data.get('carpeta_ejecutiva', False),
                'carpeta_ejecutiva_liga': data.get('carpeta_ejecutiva_liga', ''),
                'evidencias': data.get('evidencias', ''),
                'observaciones': data.get('observaciones', ''),
            }
            
            # Manejar duración personalizada
            if data.get('duracion') == 'otro':
                duracion_personalizada = data.get('duracion_personalizada')
                if not duracion_personalizada:
                    return JsonResponse({
                        'success': False,
                        'message': 'Debe especificar la duración personalizada'
                    }, status=400)
                try:
                    evento_data['duracion_personalizada'] = float(duracion_personalizada)
                except ValueError:
                    return JsonResponse({
                        'success': False,
                        'message': 'La duración personalizada debe ser un número válido'
                    }, status=400)
            
            # Crear el evento
            evento = Evento.objects.create(**evento_data)
            
            return JsonResponse({
                'success': True,
                'message': 'Evento creado correctamente',
                'evento_id': evento.id
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Error al crear evento: {str(e)}'
            }, status=500)
    
    return JsonResponse({
        'success': False,
        'message': 'Método no permitido'
    }, status=405)


@login_required
@csrf_exempt
def api_evento_detail(request, evento_id):
    """
    API para gestionar un evento específico (GET, PUT, DELETE)
    """
    try:
        evento = get_object_or_404(Evento, id=evento_id)
        user = request.user
        
        # Verificar permisos de visualización
        if not evento.puede_ver(user):
            return JsonResponse({
                'success': False,
                'message': 'No tienes permisos para acceder a este evento'
            }, status=403)
        
        if request.method == 'DELETE':
            # Verificar permisos de edición
            if not evento.puede_editar(user):
                return JsonResponse({
                    'success': False,
                    'message': 'No tienes permisos para eliminar este evento'
                }, status=403)
            
            evento.delete()
            return JsonResponse({
                'success': True,
                'message': 'Evento eliminado correctamente'
            })
        
        elif request.method == 'PUT':
            try:
                data = json.loads(request.body)
                
                # Caso especial: actualización parcial de evidencias después de que el evento terminó
                if isinstance(data, dict) and 'evidencias' in data and set(data.keys()) == {'evidencias'}:
                    if evento.ha_terminado:
                        evento.evidencias = data.get('evidencias', '')
                        evento.save(update_fields=['evidencias', 'updated_at'])
                        return JsonResponse({
                            'success': True,
                            'message': 'Evidencias actualizadas correctamente'
                        })
                    else:
                        return JsonResponse({
                            'success': False,
                            'message': 'Las evidencias solo pueden actualizarse cuando el evento haya concluido'
                        }, status=400)

                # Para actualizaciones completas, verificar permisos de edición
                if not evento.puede_editar(user):
                    return JsonResponse({
                        'success': False,
                        'message': 'No tienes permisos para editar este evento'
                    }, status=403)

                # Validar campos requeridos
                nombre_evento = data.get('nombre_evento', '').strip()
                if not nombre_evento:
                    return JsonResponse({
                        'success': False,
                        'message': 'El nombre del evento es requerido'
                    }, status=400)
                
                fecha_evento = data.get('fecha_evento')
                if not fecha_evento:
                    return JsonResponse({
                        'success': False,
                        'message': 'La fecha del evento es requerida'
                    }, status=400)
                
                hora_evento = data.get('hora_evento')
                if not hora_evento:
                    return JsonResponse({
                        'success': False,
                        'message': 'La hora del evento es requerida'
                    }, status=400)
                
                # Parsear fecha y hora
                try:
                    from datetime import datetime
                    fecha_parsed = datetime.strptime(fecha_evento, '%Y-%m-%d').date()
                    hora_parsed = datetime.strptime(hora_evento, '%H:%M').time()
                except ValueError:
                    return JsonResponse({
                        'success': False,
                        'message': 'Formato de fecha u hora inválido'
                    }, status=400)
                
                # Actualizar campos del evento
                evento.nombre_evento = nombre_evento
                evento.objetivo = data.get('objetivo', 'Por definir')
                evento.fecha_evento = fecha_parsed
                evento.hora_evento = hora_parsed
                evento.duracion = data.get('duracion', '2')
                evento.sede = data.get('sede', 'Por definir')
                evento.prioridad = data.get('prioridad', 'media')
                evento.aforo = int(data.get('aforo', 10))
                evento.link_maps = data.get('link_maps', '')
                evento.participantes = data.get('participantes', '')
                evento.carpeta_ejecutiva = data.get('carpeta_ejecutiva', False)
                evento.carpeta_ejecutiva_liga = data.get('carpeta_ejecutiva_liga', '')
                # Evidencias: editable por cualquier usuario cuando el evento ya terminó
                if evento.ha_terminado:
                    evento.evidencias = data.get('evidencias', evento.evidencias)
                evento.observaciones = data.get('observaciones', '')
                
                # Manejar duración personalizada
                if data.get('duracion') == 'otro':
                    duracion_personalizada = data.get('duracion_personalizada')
                    if not duracion_personalizada:
                        return JsonResponse({
                            'success': False,
                            'message': 'Debe especificar la duración personalizada'
                        }, status=400)
                    try:
                        evento.duracion_personalizada = float(duracion_personalizada)
                    except ValueError:
                        return JsonResponse({
                            'success': False,
                            'message': 'La duración personalizada debe ser un número válido'
                        }, status=400)
                
                # Guardar cambios
                evento.save()
                
                return JsonResponse({
                    'success': True,
                    'message': 'Evento actualizado correctamente'
                })
                
            except json.JSONDecodeError:
                return JsonResponse({
                    'success': False,
                    'message': 'Datos JSON inválidos'
                }, status=400)
        
        elif request.method == 'GET':
            return JsonResponse({
                'success': True,
                'evento': {
                    'id': evento.id,
                    'titulo': evento.nombre_evento,
                    'descripcion': evento.objetivo,
                    'fecha_inicio': evento.fecha_hora_completa.isoformat(),
                    'fecha_fin': (evento.fecha_hora_completa + timedelta(hours=evento.duracion_real)).isoformat(),
                    'ubicacion': evento.sede,
                    'prioridad': evento.prioridad,
                    'estado': evento.etapa,
                    'estado_display': evento.get_etapa_display(),
                    'usuario': {
                        'id': evento.usuario.id,
                        'nombre': evento.usuario.get_full_name() or evento.usuario.username,
                    },
                    'puede_editar': evento.puede_editar(user),
                    # Campos adicionales para la edición
                    'aforo': evento.aforo,
                    'link_maps': evento.link_maps,
                    'participantes': evento.participantes,
                    'carpeta_ejecutiva': evento.carpeta_ejecutiva,
                    'carpeta_ejecutiva_liga': evento.carpeta_ejecutiva_liga,
                    'evidencias': evento.evidencias,
                    'ha_terminado': evento.ha_terminado,
                    'observaciones': evento.observaciones,
                    'duracion': evento.duracion,
                    'duracion_personalizada': evento.duracion_personalizada,
                }
            })
            
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error: {str(e)}'
        }, status=500)
    
    return JsonResponse({
        'success': False,
        'message': 'Método no permitido'
    }, status=405)


@login_required
def api_categorias(request):
    """
    API para obtener categorías (mantenemos por compatibilidad)
    """
    if request.method == 'GET':
        try:
            # Como ya no usamos categorías, devolvemos una lista vacía o categorías por defecto
            categorias_default = [
                {'id': 1, 'nombre': 'Reunión', 'color': '#06A77D'},
                {'id': 2, 'nombre': 'Evento', 'color': '#3B82F6'},
                {'id': 3, 'nombre': 'Tarea', 'color': '#EF4444'},
                {'id': 4, 'nombre': 'Otro', 'color': '#6B7280'},
            ]
            
            return JsonResponse({
                'success': True,
                'categorias': categorias_default
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Error al obtener categorías: {str(e)}'
            }, status=500)
    
    return JsonResponse({
        'success': False,
        'message': 'Método no permitido'
    }, status=405)
