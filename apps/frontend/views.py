"""
Vistas del frontend para login y dashboard
Sistema completo de autenticación con 3 niveles de usuario
Solo administradores pueden crear usuarios
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.csrf import csrf_protect
from django.http import JsonResponse
from django.http import HttpResponse
from django.views.decorators.http import require_http_methods
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView, View
from django.core.paginator import Paginator
from django.db.models import Q
from apps.authentication.models import User
from .forms import AdminUserCreateForm, AdminUserEditForm, UserSearchForm
import json
from django.utils import timezone

class EventosUsuariosStatsView(TemplateView):
    template_name = 'frontend/eventos_usuarios_stats.html'

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        if not (request.user.is_admin() or request.user.is_manager()):
            return redirect('frontend:dashboard')
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from apps.eventos.models import Evento
        req = self.request

        # Parámetros
        q = req.GET.get('q', '').strip()
        prioridad = req.GET.get('prioridad', '').strip().lower()
        fecha_desde_raw = req.GET.get('desde', '').strip()
        fecha_hasta_raw = req.GET.get('hasta', '').strip()
        usuario_filter = req.GET.get('usuario', '').strip()

        qs = Evento.objects.select_related('usuario').all()
        if q:
            qs = qs.filter(nombre_evento__icontains=q)
        if prioridad in {'baja','media','alta','urgente'}:
            qs = qs.filter(prioridad=prioridad)
        if usuario_filter.isdigit():
            qs = qs.filter(usuario_id=int(usuario_filter))

        # Fechas
        from datetime import datetime
        def parse_date(v):
            for fmt in ('%Y-%m-%d','%d/%m/%Y'):
                try:
                    return datetime.strptime(v, fmt).date()
                except Exception:
                    continue
            return None
        d_desde = parse_date(fecha_desde_raw) if fecha_desde_raw else None
        d_hasta = parse_date(fecha_hasta_raw) if fecha_hasta_raw else None
        if d_desde:
            qs = qs.filter(fecha_evento__gte=d_desde)
        if d_hasta:
            qs = qs.filter(fecha_evento__lte=d_hasta)

        filtros_aplicados = {
            'q': q,
            'prioridad': prioridad,
            'desde': fecha_desde_raw,
            'hasta': fecha_hasta_raw,
            'usuario': usuario_filter,
        }

        # Agregaciones ORM
        from django.db.models import Count, Q as _Q, Subquery, OuterRef, F, Sum
        from django.db.models.expressions import RawSQL
        from datetime import timedelta
        ahora = timezone.now()
        today = timezone.localdate()
        current_year, current_month = today.year, today.month

        # Subquery para último evento (fecha, hora, nombre)
        last_events = (Evento.objects
                        .filter(usuario_id=OuterRef('usuario_id'))
                        .order_by('-fecha_evento', '-hora_evento'))

        # Flag de finalización calculado en SQL (PostgreSQL): 1 si el evento terminó (fin < NOW())
        ended_raw = RawSQL(
            "CASE WHEN (fecha_evento + hora_evento + ((CASE WHEN duracion = 'otro' THEN COALESCE(duracion_personalizada,0)::text ELSE duracion END)||' hours')::interval) < NOW() THEN 1 ELSE 0 END",
            []
        )

        agregados_qs = (qs
            .values('usuario_id', 'usuario__first_name', 'usuario__last_name', 'usuario__username', 'usuario__email')
            .annotate(
                total=Count('id'),
                urgentes=Count('id', filter=_Q(prioridad='urgente')),
                mes_actual=Count('id', filter=_Q(fecha_evento__year=current_year, fecha_evento__month=current_month)),
                last_fecha=Subquery(last_events.values('fecha_evento')[:1]),
                last_hora=Subquery(last_events.values('hora_evento')[:1]),
                last_nombre=Subquery(last_events.values('nombre_evento')[:1]),
                _ended_sum=Sum(ended_raw),
            ))

        filas = []
        current_month_counts = {}
        for row in agregados_qs:
            full_name = (row['usuario__first_name'] + ' ' + row['usuario__last_name']).strip()
            if not full_name:
                full_name = row['usuario__username']
            email = row['usuario__email']
            uid = row['usuario_id']
            last_display = '—'
            last_nombre = '—'
            if row['last_fecha'] and row['last_hora']:
                from datetime import datetime as _dt
                dt_combined = _dt.combine(row['last_fecha'], row['last_hora'])
                if timezone.is_naive(dt_combined):
                    dt_combined = timezone.make_aware(dt_combined, timezone.get_current_timezone())
                last_display = dt_combined.strftime('%d/%m/%Y %H:%M')
                last_nombre = row['last_nombre'] or '—'
            completados = row.get('_ended_sum') or 0
            activos = row['total'] - completados
            filas.append({
                'usuario': full_name,
                'email': email,
                'total': row['total'],
                'activos': activos,
                'completados': completados,
                'urgentes': row['urgentes'],
                'ultimo': last_display,
                'ultimo_nombre': last_nombre,
                'mes_actual': row['mes_actual'],
            })
            if row['mes_actual']:
                current_month_counts[uid] = {'usuario': full_name, 'count': row['mes_actual']}

        filas.sort(key=lambda x: x['total'], reverse=True)
        total_eventos_sum = sum(f['total'] for f in filas)
        # --- Gráfica con modos (mes actual, últimos 3, últimos 12) ---
        import json as _json
        chart_mode = self.request.GET.get('chart', 'mes')
        allowed_modes = {'mes','3m','12m'}
        if chart_mode not in allowed_modes:
            chart_mode = 'mes'

        meses_es_corto = ['Ene','Feb','Mar','Abr','May','Jun','Jul','Ago','Sep','Oct','Nov','Dic']
        meses_es = ['Enero','Febrero','Marzo','Abril','Mayo','Junio','Julio','Agosto','Septiembre','Octubre','Noviembre','Diciembre']

        chart_payload = {'mode': chart_mode}

        if chart_mode == 'mes':
            rows_mes = sorted(current_month_counts.values(), key=lambda x: x['count'], reverse=True)
            chart_payload.update({
                'labels': [r['usuario'] for r in rows_mes],
                'counts': [r['count'] for r in rows_mes],
                'title': f"Eventos mes actual ({meses_es[current_month-1]} {current_year})"
            })
        else:
            # Construir rango de meses
            rango = 3 if chart_mode == '3m' else 12
            # Lista de (year, month) desde más antiguo a actual
            y, m = current_year, current_month
            pares = []
            for _ in range(rango):
                pares.append((y, m))
                m -= 1
                if m == 0:
                    m = 12
                    y -= 1
            pares.reverse()  # cronológico
            base_counts = {f"{yy}-{mm:02d}": 0 for (yy, mm) in pares}
            # Contar eventos por mes usando ORM
            from django.db.models.functions import ExtractYear, ExtractMonth
            mensual = (qs
                       .values(anio=ExtractYear('fecha_evento'), mes=ExtractMonth('fecha_evento'))
                       .annotate(c=Count('id')))
            for item in mensual:
                key = f"{item['anio']}-{item['mes']:02d}"
                if key in base_counts:
                    base_counts[key] = item['c']
            labels = [f"{meses_es_corto[mm-1]} {str(yy)[2:]}" for (yy, mm) in pares]
            counts = [base_counts[f"{yy}-{mm:02d}"] for (yy, mm) in pares]
            chart_payload.update({
                'labels': labels,
                'counts': counts,
                'title': 'Eventos últimos ' + ('3 meses' if chart_mode == '3m' else '12 meses')
            })

        chart_json = _json.dumps(chart_payload)

        # Export CSV
        if req.GET.get('export') == 'csv':
            return self._export_csv(filas, total_eventos_sum)

        # Paginación
        from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
        try:
            page_size = int(req.GET.get('page_size', 25))
        except ValueError:
            page_size = 25
        page_size = max(1, min(page_size, 500))
        paginator = Paginator(filas, page_size)
        page_number = req.GET.get('page', 1)
        try:
            page_obj = paginator.page(page_number)
        except PageNotAnInteger:
            page_obj = paginator.page(1)
        except EmptyPage:
            page_obj = paginator.page(paginator.num_pages)

        base_params = []
        for key in ['q','prioridad','desde','hasta','usuario','page_size','chart']:
            val = filtros_aplicados.get(key) if key != 'page_size' else page_size
            if key == 'chart':
                val = chart_mode
            if val:
                base_params.append(f"{key}={val}")
        querystring = '&'.join(base_params)

        context.update({
            'title': 'Estadísticas de Eventos por Usuario',
            'filas': page_obj.object_list,
            'page_obj': page_obj,
            'is_paginated': page_obj.paginator.num_pages > 1,
            'paginator': page_obj.paginator,
            'page_size': page_size,
            'page_sizes': [10,25,50,100,200],
            'total_usuarios_con_eventos': len(filas),
            'total_eventos_sum': total_eventos_sum,
            'filtros_aplicados': filtros_aplicados,
            'prioridades_opciones': ['baja','media','alta','urgente'],
            'usuarios_opciones': self._get_usuario_opciones(),
            'querystring': querystring,
            'chart_json': chart_json,
            'chart_mode': chart_mode,
            'chart_debug': chart_payload,
        })
        return context

    def _export_csv(self, filas, total_eventos_sum):
        import csv
        from io import StringIO
        buffer = StringIO()
        writer = csv.writer(buffer)
        writer.writerow(['Usuario','Email','Total','Activos','Completados','Urgentes','Ultimo Evento','Titulo Ultimo'])
        for f in filas:
            writer.writerow([
                f['usuario'], f['email'], f['total'], f['activos'], f['completados'], f['urgentes'], f['ultimo'], f['ultimo_nombre']
            ])
        writer.writerow([])
        writer.writerow(['TOTAL EVENTOS', total_eventos_sum])
        resp = HttpResponse(buffer.getvalue(), content_type='text/csv; charset=utf-8')
        resp['Content-Disposition'] = 'attachment; filename="eventos_por_usuario.csv"'
        return resp

    def _get_usuario_opciones(self):
        from apps.authentication.models import User
        user = self.request.user
        qs = User.objects.all()
        if user.is_manager() and not user.is_admin():
            qs = qs.filter(user_level__in=['USER','MANAGER'])
        return [
            {
                'id': u.id,
                'nombre': u.get_full_name() or u.username,
            } for u in qs.order_by('first_name','last_name','username')
        ]


class HomeView(TemplateView):
    """Vista principal que redirige según el estado de autenticación"""
    template_name = 'frontend/login.html'
    
    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('frontend:dashboard')
        return super().get(request, *args, **kwargs)


class LoginView(TemplateView):
    """
    Vista de login con diseño personalizado
    Solo administradores pueden crear nuevos usuarios
    """
    template_name = 'frontend/login.html'
    
    def get(self, request, *args, **kwargs):
        # Si el usuario ya está autenticado, redirigir al dashboard
        if request.user.is_authenticated:
            return redirect('frontend:dashboard')
        return super().get(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'title': 'Iniciar Sesión - Mindara',
            'show_register_link': False,  # No mostrar enlace de registro
        })
        return context


@method_decorator(login_required, name='dispatch')
class DashboardView(TemplateView):
    """
    Dashboard principal según el nivel del usuario
    """
    template_name = 'frontend/dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        # Estadísticas según el nivel del usuario
        stats = self.get_user_stats(user)
        
        # Importar modelos de eventos para estadísticas
        try:
            from apps.eventos.models import Evento
            eventos_stats = self.get_eventos_stats(user)
            stats.update(eventos_stats)
        except ImportError:
            pass
        
        context.update({
            'title': f'Dashboard - {user.get_user_level_display()}',
            'user': user,
            'user_stats': stats,
            'can_manage_users': user.can_manage_users(),
            'is_admin': user.is_admin(),
            'is_manager': user.is_manager(),
            'is_basic_user': user.is_basic_user(),
            'total_users': stats.get('total_users', 0),
            'total_eventos': stats.get('total_eventos', 0),
            'total_managers': stats.get('manager_users', 0),
            'total_regular_users': stats.get('basic_users', 0),
            'recent_users': self.get_recent_users(user) if user.is_admin() else [],
        })
        return context
    
    def get_user_stats(self, user):
        """
        Obtener estadísticas según el nivel del usuario
        """
        stats = {
            'own_profile': True,
            'can_view_users': False,
            'total_users': 0,
            'manageable_users': 0,
        }
        
        if user.is_admin():
            # Los admins pueden ver todo
            stats.update({
                'can_view_users': True,
                'total_users': User.objects.count(),
                'active_users': User.objects.filter(is_active=True).count(),
                'admin_users': User.objects.filter(user_level='ADMIN').count(),
                'manager_users': User.objects.filter(user_level='MANAGER').count(),
                'basic_users': User.objects.filter(user_level='USER').count(),
                'manageable_users': User.objects.count(),
            })
        elif user.is_manager():
            # Los managers solo pueden ver usuarios básicos
            basic_users = User.objects.filter(user_level='USER')
            stats.update({
                'can_view_users': True,
                'total_users': basic_users.count(),
                'manageable_users': basic_users.count(),
                'basic_users': basic_users.count(),
            })
        
        return stats
    
    def get_eventos_stats(self, user):
        """
        Obtener estadísticas de eventos
        """
        from apps.eventos.models import Evento
        
        if user.is_admin():
            # Administradores ven todos los eventos
            total_eventos = Evento.objects.count()
            eventos_activos = Evento.objects.filter(etapa__in=['planificacion', 'revision', 'confirmado']).count()
        elif user.is_manager():
            # Managers ven eventos de usuarios básicos y propios
            total_eventos = Evento.objects.filter(
                usuario__user_level__in=['USER', 'MANAGER']
            ).count()
            eventos_activos = Evento.objects.filter(
                usuario__user_level__in=['USER', 'MANAGER'],
                etapa__in=['planificacion', 'revision', 'confirmado']
            ).count()
        else:
            # Usuarios básicos solo ven sus propios eventos
            total_eventos = Evento.objects.filter(usuario=user).count()
            eventos_activos = Evento.objects.filter(
                usuario=user,
                etapa__in=['planificacion', 'revision', 'confirmado']
            ).count()
        
        return {
            'total_eventos': total_eventos,
            'eventos_activos': eventos_activos,
        }
    
    def get_recent_users(self, user):
        """
        Obtener usuarios recientes (solo para administradores)
        """
        if not user.is_admin():
            return []
        
        return User.objects.order_by('-last_login', '-date_joined')[:5]


@csrf_protect
@require_http_methods(["POST"])
def login_api(request):
    """
    API de login para AJAX
    """
    try:
        data = json.loads(request.body)
        email = data.get('email')
        password = data.get('password')
        
        if not email or not password:
            return JsonResponse({
                'success': False,
                'message': 'Email y contraseña son requeridos'
            }, status=400)
        
        # Autenticar con email (que es el USERNAME_FIELD)
        user = authenticate(request, username=email, password=password)
        
        if user is not None:
            if user.is_active:
                login(request, user)
                return JsonResponse({
                    'success': True,
                    'message': f'¡Bienvenido {user.get_full_name() or user.username}!',
                    'redirect_url': '/dashboard/',
                    'user': {
                        'id': user.id,
                        'username': user.username,
                        'email': user.email,
                        'full_name': user.get_full_name(),
                        'level': user.user_level,
                        'level_display': user.get_user_level_display(),
                        'is_admin': user.is_admin(),
                        'is_manager': user.is_manager(),
                        'can_manage_users': user.can_manage_users(),
                    }
                })
            else:
                return JsonResponse({
                    'success': False,
                    'message': 'Tu cuenta está desactivada. Contacta al administrador.'
                }, status=403)
        else:
            return JsonResponse({
                'success': False,
                'message': 'Credenciales incorrectas'
            }, status=401)
            
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'message': 'Datos de entrada inválidos'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': 'Error interno del servidor'
        }, status=500)


@login_required
def logout_view(request):
    """
    Vista para cerrar sesión
    """
    logout(request)
    messages.success(request, 'Sesión cerrada exitosamente')
    return redirect('frontend:login')


# API Views para AJAX

@csrf_protect
@require_http_methods(["GET"])
@login_required
def user_profile_api(request):
    """
    API para obtener información del perfil del usuario
    """
    user = request.user
    
    return JsonResponse({
        'success': True,
        'user': {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'full_name': user.get_full_name(),
            'level': user.user_level,
            'level_display': user.get_user_level_display(),
            'is_admin': user.is_admin(),
            'is_manager': user.is_manager(),
            'can_manage_users': user.can_manage_users(),
            'date_joined': user.date_joined.isoformat(),
            'last_login': user.last_login.isoformat() if user.last_login else None,
            'is_active': user.is_active,
        }
    })


@csrf_protect  
@require_http_methods(["GET"])
@login_required
def dashboard_stats_api(request):
    """
    API para obtener estadísticas del dashboard
    """
    user = request.user
    
    if user.is_admin():
        # Estadísticas completas para administradores
        stats = {
            'total_users': User.objects.count(),
            'active_users': User.objects.filter(is_active=True).count(),
            'inactive_users': User.objects.filter(is_active=False).count(),
            'admin_users': User.objects.filter(user_level='ADMIN').count(),
            'manager_users': User.objects.filter(user_level='MANAGER').count(),
            'basic_users': User.objects.filter(user_level='USER').count(),
            'recent_users': list(User.objects.order_by('-date_joined')[:5].values(
                'id', 'username', 'email', 'first_name', 'last_name', 'user_level', 'date_joined'
            )),
        }
    elif user.is_manager():
        # Estadísticas limitadas para managers
        basic_users = User.objects.filter(user_level='USER')
        stats = {
            'total_users': basic_users.count(),
            'active_users': basic_users.filter(is_active=True).count(),
            'inactive_users': basic_users.filter(is_active=False).count(),
            'basic_users': basic_users.count(),
            'recent_users': list(basic_users.order_by('-date_joined')[:5].values(
                'id', 'username', 'email', 'first_name', 'last_name', 'user_level', 'date_joined'
            )),
        }
    else:
        # Solo información personal para usuarios básicos
        stats = {
            'own_profile': True,
            'level': user.user_level,
            'date_joined': user.date_joined.isoformat(),
        }
    
    return JsonResponse({
        'success': True,
        'stats': stats
    })


@method_decorator(login_required, name='dispatch')
class AyudaView(TemplateView):
    """
    Vista de la página de ayuda del sistema
    Accesible para todos los usuarios autenticados
    """
    template_name = 'frontend/ayuda.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'title': 'Centro de Ayuda - Mindara',
        })
        return context


@method_decorator(login_required, name='dispatch')
class TerminosView(TemplateView):
    """Página de Términos y Licencia (Apache-2.0)"""
    template_name = 'frontend/terminos.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'title': 'Términos y Licencia - Mindara',
            'ultima_actualizacion': 'Agosto 2025',
        })
        return context


# === VISTAS DE ADMINISTRACIÓN DE USUARIOS ===

@method_decorator(login_required, name='dispatch')
class UserManagementView(TemplateView):
    """
    Vista principal de gestión de usuarios (solo para administradores)
    """
    template_name = 'frontend/user_management.html'
    
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_admin():
            messages.error(request, 'No tienes permisos para acceder a esta sección.')
            return redirect('frontend:dashboard')
        return super().dispatch(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Formulario de búsqueda
        search_form = UserSearchForm(self.request.GET)
        
        # Obtener usuarios con filtros
        users_queryset = User.objects.all().order_by('-date_joined')
        
        if search_form.is_valid():
            search = search_form.cleaned_data.get('search')
            user_level = search_form.cleaned_data.get('user_level')
            is_active = search_form.cleaned_data.get('is_active')
            
            if search:
                users_queryset = users_queryset.filter(
                    Q(username__icontains=search) |
                    Q(email__icontains=search) |
                    Q(first_name__icontains=search) |
                    Q(last_name__icontains=search)
                )
            
            if user_level:
                users_queryset = users_queryset.filter(user_level=user_level)
            
            if is_active:
                users_queryset = users_queryset.filter(is_active=is_active == 'true')
        
        # Paginación
        paginator = Paginator(users_queryset, 20)
        page_number = self.request.GET.get('page')
        users = paginator.get_page(page_number)
        
        # Estadísticas
        stats = {
            'total_users': User.objects.count(),
            'active_users': User.objects.filter(is_active=True).count(),
            'admin_users': User.objects.filter(user_level='ADMIN').count(),
            'manager_users': User.objects.filter(user_level='MANAGER').count(),
            'basic_users': User.objects.filter(user_level='USER').count(),
        }
        
        context.update({
            'title': 'Gestión de Usuarios - Administración',
            'users': users,
            'search_form': search_form,
            'stats': stats,
        })
        return context


@method_decorator(login_required, name='dispatch')
class CreateUserView(View):
    """
    Vista para crear nuevos usuarios (solo administradores)
    """
    template_name = 'frontend/create_user.html'
    
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_admin():
            messages.error(request, 'No tienes permisos para crear usuarios.')
            return redirect('frontend:dashboard')
        return super().dispatch(request, *args, **kwargs)
    
    def get(self, request):
        form = AdminUserCreateForm()
        return render(request, self.template_name, {
            'title': 'Crear Nuevo Usuario',
            'form': form,
        })
    
    def post(self, request):
        form = AdminUserCreateForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, f'Usuario {user.username} creado exitosamente.')
            return redirect('frontend:user_management')
        
        return render(request, self.template_name, {
            'title': 'Crear Nuevo Usuario',
            'form': form,
        })


@method_decorator(login_required, name='dispatch')
class EditUserView(View):
    """
    Vista para editar usuarios existentes (solo administradores)
    """
    template_name = 'frontend/edit_user.html'
    
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_admin():
            messages.error(request, 'No tienes permisos para editar usuarios.')
            return redirect('frontend:dashboard')
        return super().dispatch(request, *args, **kwargs)
    
    def get(self, request, user_id):
        user = get_object_or_404(User, id=user_id)
        form = AdminUserEditForm(instance=user)
        return render(request, self.template_name, {
            'title': f'Editar Usuario: {user.username}',
            'form': form,
            'edited_user': user,
        })
    
    def post(self, request, user_id):
        user = get_object_or_404(User, id=user_id)
        form = AdminUserEditForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, f'Usuario {user.username} actualizado exitosamente.')
            return redirect('frontend:user_management')
        
        return render(request, self.template_name, {
            'title': f'Editar Usuario: {user.username}',
            'form': form,
            'edited_user': user,
        })


@csrf_protect
@require_http_methods(["POST"])
@login_required
def toggle_user_status(request, user_id):
    """
    API para activar/desactivar usuarios
    """
    if not request.user.is_admin():
        return JsonResponse({
            'success': False,
            'message': 'No tienes permisos para realizar esta acción.'
        }, status=403)
    
    try:
        user = get_object_or_404(User, id=user_id)
        
        # No permitir desactivar al propio usuario
        if user == request.user:
            return JsonResponse({
                'success': False,
                'message': 'No puedes desactivar tu propia cuenta.'
            }, status=400)
        
        user.is_active = not user.is_active
        user.save()
        
        status_text = 'activado' if user.is_active else 'desactivado'
        
        return JsonResponse({
            'success': True,
            'message': f'Usuario {user.username} {status_text} exitosamente.',
            'is_active': user.is_active
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': 'Error al cambiar el estado del usuario.'
        }, status=500)


@csrf_protect
@require_http_methods(["DELETE"])
@login_required
def delete_user(request, user_id):
    """
    API para eliminar usuarios (solo administradores)
    """
    if not request.user.is_admin():
        return JsonResponse({
            'success': False,
            'message': 'No tienes permisos para eliminar usuarios.'
        }, status=403)
    
    try:
        user = get_object_or_404(User, id=user_id)
        
        # No permitir eliminar al propio usuario
        if user == request.user:
            return JsonResponse({
                'success': False,
                'message': 'No puedes eliminar tu propia cuenta.'
            }, status=400)
        
        username = user.username
        user.delete()
        
        return JsonResponse({
            'success': True,
            'message': f'Usuario {username} eliminado exitosamente.'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': 'Error al eliminar el usuario.'
        }, status=500)
