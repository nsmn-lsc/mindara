"""
Vistas para el módulo de notificaciones
"""

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from django.urls import reverse_lazy
from django.db.models import Q
from django.core.paginator import Paginator

from apps.authentication.permissions import AdminManagerPermissionMixin
from .models import Notificacion, NotificacionLeida
from .forms import NotificacionForm, NotificacionRapidaForm


class NotificacionListView(LoginRequiredMixin, ListView):
    """Vista para listar notificaciones (solo para admins y managers)"""
    model = Notificacion
    template_name = 'notificaciones/lista.html'
    context_object_name = 'notificaciones'
    paginate_by = 20
    
    def dispatch(self, request, *args, **kwargs):
        if not request.user.user_level in ['ADMIN', 'MANAGER']:
            messages.error(request, 'No tienes permisos para acceder a esta sección.')
            return redirect('frontend:dashboard')
        return super().dispatch(request, *args, **kwargs)
    
    def get_queryset(self):
        return Notificacion.objects.all().order_by('-fecha_creacion')


class NotificacionCreateView(AdminManagerPermissionMixin, CreateView):
    """Vista para crear nuevas notificaciones"""
    model = Notificacion
    form_class = NotificacionForm
    template_name = 'notificaciones/crear.html'
    success_url = reverse_lazy('notificaciones:lista')
    
    def form_valid(self, form):
        form.instance.creado_por = self.request.user
        response = super().form_valid(form)
        messages.success(self.request, 'Notificación creada exitosamente.')
        return response


class NotificacionRapidaCreateView(AdminManagerPermissionMixin, CreateView):
    """
    Vista para crear notificaciones rápidas (formulario simplificado)
    """
    model = Notificacion
    form_class = NotificacionRapidaForm
    template_name = 'notificaciones/crear_rapida.html'
    success_url = reverse_lazy('notificaciones:lista')
    
    def form_valid(self, form):
        form.instance.creado_por = self.request.user
        response = super().form_valid(form)
        
        messages.success(
            self.request, 
            f'Notificación rápida "{form.instance.titulo}" enviada exitosamente.'
        )
        return response


class NotificacionUpdateView(AdminManagerPermissionMixin, UpdateView):
    """Vista para editar notificaciones"""
    model = Notificacion
    form_class = NotificacionForm
    template_name = 'notificaciones/editar.html'
    success_url = reverse_lazy('notificaciones:lista')
    
    def form_valid(self, form):
        # Manejar el campo activa manualmente si está en POST
        if 'activa' in self.request.POST:
            form.instance.activa = True
        else:
            form.instance.activa = False
            
        response = super().form_valid(form)
        messages.success(self.request, 'Notificación actualizada exitosamente.')
        return response


class NotificacionDeleteView(AdminManagerPermissionMixin, DeleteView):
    """Vista para eliminar notificaciones"""
    model = Notificacion
    template_name = 'notificaciones/eliminar.html'
    success_url = reverse_lazy('notificaciones:lista')
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Notificación eliminada exitosamente.')
        return super().delete(request, *args, **kwargs)


@login_required
def mis_notificaciones(request):
    """Vista para que los usuarios vean sus notificaciones"""
    user = request.user
    
    # Obtener todas las notificaciones que el usuario puede ver
    notificaciones_base = Notificacion.objects.filter(activa=True)
    
    # Filtrar notificaciones no expiradas
    notificaciones_base = notificaciones_base.filter(
        Q(fecha_expiracion__isnull=True) | Q(fecha_expiracion__gt=timezone.now())
    )
    
    # Filtrar por targeting
    notificaciones_visibles = notificaciones_base.filter(
        Q(usuarios_objetivo=user) |  # Usuario específico
        Q(nivel_usuario_objetivo=user.user_level) |  # Por nivel de usuario
        Q(usuarios_objetivo__isnull=True, nivel_usuario_objetivo__isnull=True)  # Para todos
    ).distinct()
    
    # Aplicar filtros de búsqueda
    buscar = request.GET.get('buscar', '')
    tipo = request.GET.get('tipo', '')
    estado = request.GET.get('estado', '')
    
    if buscar:
        notificaciones_visibles = notificaciones_visibles.filter(
            Q(titulo__icontains=buscar) | Q(mensaje__icontains=buscar)
        )
    
    if tipo:
        notificaciones_visibles = notificaciones_visibles.filter(tipo=tipo)
    
    # Crear lista con información de lectura
    notificaciones_con_lectura = []
    for notif in notificaciones_visibles.order_by('-fecha_creacion'):
        try:
            lectura = NotificacionLeida.objects.get(notificacion=notif, usuario=user)
            notificaciones_con_lectura.append({
                'notificacion': notif,
                'leida': True,
                'fecha_lectura': lectura.fecha_lectura
            })
        except NotificacionLeida.DoesNotExist:
            notificaciones_con_lectura.append({
                'notificacion': notif,
                'leida': False,
                'fecha_lectura': None
            })
    
    # Filtrar por estado de lectura si se especifica
    if estado == 'no_leidas':
        notificaciones_con_lectura = [n for n in notificaciones_con_lectura if not n['leida']]
    elif estado == 'leidas':
        notificaciones_con_lectura = [n for n in notificaciones_con_lectura if n['leida']]
    
    # Paginación
    paginator = Paginator(notificaciones_con_lectura, 10)
    page_number = request.GET.get('page')
    notificaciones = paginator.get_page(page_number)
    
    # Estadísticas
    total_notificaciones = len(notificaciones_con_lectura)
    no_leidas_count = len([n for n in notificaciones_con_lectura if not n['leida']])
    leidas_count = total_notificaciones - no_leidas_count
    
    context = {
        'notificaciones': notificaciones,
        'total_notificaciones': total_notificaciones,
        'no_leidas_count': no_leidas_count,
        'leidas_count': leidas_count,
        'is_paginated': paginator.num_pages > 1,
        'page_obj': notificaciones,
    }
    
    return render(request, 'notificaciones/mis_notificaciones.html', context)


@login_required
def marcar_como_leida(request):
    """AJAX: Marcar notificación como leída"""
    if request.method == 'POST':
        notificacion_id = request.POST.get('notificacion_id')
        try:
            notificacion = get_object_or_404(Notificacion, id=notificacion_id)
            
            # Verificar que el usuario puede ver esta notificación
            if not puede_ver_notificacion(request.user, notificacion):
                return JsonResponse({'success': False, 'error': 'No autorizado'})
            
            # Crear o obtener el registro de lectura
            lectura, created = NotificacionLeida.objects.get_or_create(
                notificacion=notificacion,
                usuario=request.user
            )
            
            return JsonResponse({
                'success': True,
                'leida': True,
                'fecha_lectura': lectura.fecha_lectura.strftime('%d/%m/%Y %H:%M')
            })
            
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Método no permitido'})


@login_required
def marcar_todas_como_leidas(request):
    """AJAX: Marcar todas las notificaciones del usuario como leídas"""
    if request.method == 'POST':
        try:
            user = request.user
            
            # Obtener notificaciones visibles para el usuario
            notificaciones_visibles = Notificacion.objects.filter(
                activa=True
            ).filter(
                Q(fecha_expiracion__isnull=True) | Q(fecha_expiracion__gt=timezone.now())
            ).filter(
                Q(usuarios_objetivo=user) |
                Q(nivel_usuario_objetivo=user.user_level) |
                Q(usuarios_objetivo__isnull=True, nivel_usuario_objetivo__isnull=True)
            ).distinct()
            
            # Obtener las que no ha leído
            leidas_ids = NotificacionLeida.objects.filter(
                usuario=user
            ).values_list('notificacion_id', flat=True)
            
            no_leidas = notificaciones_visibles.exclude(id__in=leidas_ids)
            marcadas = 0
            
            for notificacion in no_leidas:
                NotificacionLeida.objects.get_or_create(
                    notificacion=notificacion,
                    usuario=user
                )
                marcadas += 1
            
            return JsonResponse({
                'success': True,
                'marcadas': marcadas
            })
            
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Método no permitido'})


@login_required
def obtener_notificaciones_no_leidas(request):
    """AJAX: Obtener contador de notificaciones no leídas"""
    try:
        user = request.user
        
        # Obtener notificaciones visibles para el usuario
        notificaciones_visibles = Notificacion.objects.filter(
            activa=True
        ).filter(
            Q(fecha_expiracion__isnull=True) | Q(fecha_expiracion__gt=timezone.now())
        ).filter(
            Q(usuarios_objetivo=user) |
            Q(nivel_usuario_objetivo=user.user_level) |
            Q(usuarios_objetivo__isnull=True, nivel_usuario_objetivo__isnull=True)
        ).distinct()
        
        # Obtener IDs de notificaciones leídas
        leidas_ids = NotificacionLeida.objects.filter(
            usuario=user
        ).values_list('notificacion_id', flat=True)
        
        # Contar no leídas
        no_leidas_count = notificaciones_visibles.exclude(id__in=leidas_ids).count()
        
        # Obtener las últimas 5 notificaciones no leídas para el dropdown
        ultimas_no_leidas = notificaciones_visibles.exclude(id__in=leidas_ids).order_by('-fecha_creacion')[:5]
        
        notificaciones_data = []
        for notif in ultimas_no_leidas:
            notificaciones_data.append({
                'id': notif.id,
                'titulo': notif.titulo,
                'mensaje': notif.mensaje[:100] + '...' if len(notif.mensaje) > 100 else notif.mensaje,
                'tipo': notif.tipo,
                'prioridad': notif.prioridad,
                'fecha_creacion': notif.fecha_creacion.strftime('%d/%m/%Y %H:%M'),
            })
        
        return JsonResponse({
            'success': True,
            'cantidad': no_leidas_count,
            'notificaciones': notificaciones_data
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


def puede_ver_notificacion(usuario, notificacion):
    """Función auxiliar para verificar si un usuario puede ver una notificación"""
    if not notificacion.activa:
        return False
    
    if notificacion.fecha_expiracion and timezone.now() > notificacion.fecha_expiracion:
        return False
    
    # Verificar targeting
    if notificacion.usuarios_objetivo.filter(id=usuario.id).exists():
        return True
    
    if notificacion.nivel_usuario_objetivo == usuario.user_level:
        return True
    
    if not notificacion.usuarios_objetivo.exists() and not notificacion.nivel_usuario_objetivo:
        return True
    
    return False


@login_required
def toggle_notificacion_estado(request, notificacion_id):
    """AJAX: Activar/desactivar notificación (solo admins/managers)"""
    if request.method == 'POST' and request.user.user_level in ['ADMIN', 'MANAGER']:
        try:
            notificacion = get_object_or_404(Notificacion, id=notificacion_id)
            notificacion.activa = not notificacion.activa
            notificacion.save()
            
            return JsonResponse({
                'success': True,
                'activa': notificacion.activa,
                'mensaje': 'Activada' if notificacion.activa else 'Desactivada'
            })
            
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'No autorizado'})
