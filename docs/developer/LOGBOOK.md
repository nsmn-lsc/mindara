# Logbook (Bitácora de Desarrollo)

Registro narrativo día a día de cambios relevantes, decisiones y próximos pasos.

## 2025-08-14
**Contexto:** Consolidación legal y de estáticos tras creación de dashboard de estadísticas en días previos.

**Cambios Clave:**
- Merge a `main` integrando: página de Términos, LICENSE, NOTICE, normalización de `static/`.
- Inclusión de FullCalendar en repositorio para evitar 404.
- Ajuste `.gitignore` para versionar assets fuente.
- Validación `collectstatic` con manifest local (sin errores) y despliegue con fallback en Render.

**Decisiones:**
- Mantener variables `FORCE_SIMPLE_STATIC` y `DISABLE_MANIFEST_STATIC` temporalmente hasta verificación manual completa.
- Adoptar SemVer iniciando con hito `0.2.0` por cambio estructural de estáticos y licencia pública.

**Riesgos / Observaciones:**
- Falta activar caché con hashing definitivo (pendiente retirar fallback).
- Política de Privacidad aún placeholder.

**Próximos Pasos Sugeridos:**
1. Validar producción (assets, headers seguridad, /terminos/).
2. Quitar fallback estáticos y redeploy.
3. Añadir Política de Privacidad.
4. Configurar CSP básica y versionado de release (tag `v0.2.0`).

---

## Formato Futuro
Cada fecha incluirá: Contexto, Cambios, Decisiones, Riesgos, Próximos Pasos.

## 2025-08-15
**Contexto:** Endurecimiento de seguridad de sesiones y corrección de métricas del dashboard tras release 0.2.0.

**Cambios Clave:**
- Dashboard: reemplazo de valores estáticos (eventos=5, usuarios=12) por carga dinámica vía `/api/dashboard-stats/` incluyendo eventos activos, totales y notificaciones activas.
- API `dashboard_stats_api`: ampliada con `events_total`, `events_active`, `notifications_active` adaptados por rol (admin/manager/usuario).
- Gestión de sesión: añadido `IdleSessionMiddleware` con timeout de inactividad configurable (`IDLE_SESSION_TIMEOUT`), expiración al cerrar navegador (`SESSION_EXPIRE_AT_BROWSER_CLOSE=True`) y renovación sliding (`SESSION_SAVE_EVERY_REQUEST=True`).
- Mensaje de expiración: redirección a `/login/?expired=1` y alerta informativa; respuestas JSON 401 con `code=session_expired` para peticiones AJAX.
- Fix despliegue: reordenado middleware después de `AuthenticationMiddleware` para evitar `AttributeError` en `/healthz`.
- Documentación: creación de notas de release `docs/release/v0.2.0.md`, `CHANGELOG.md` inicial y script de mantenimiento de changelog.
- Etiqueta `v0.2.0` publicada.

**Decisiones:**
- Mantener timeout por defecto 30 minutos; permitir ajuste vía variable de entorno para entornos sensibles.
- Mantener fallback estáticos una iteración más antes de activar `CompressedManifestStaticFilesStorage` definitivo.
- Implementar mensaje de expiración simple (alerta) antes de considerar modal de pre-expiración.

**Riesgos / Observaciones:**
- Usuarios podrían confundir expiración silenciosa si cierran solo pestaña (alerta mitiga una parte).
- Fallback estático prolongado retrasa cache busting óptimo (recordatorio para próxima iteración).
- Falta Política de Privacidad y cabecera CSP.

**Próximos Pasos Sugeridos:**
1. Activar manifest y compresión (remover variables de fallback) tras validar logs sin 404.
2. Añadir modal de aviso 1–2 minutos antes de expirar (opcional) y botón “Mantener sesión”.
3. Implementar Política de Privacidad y enlazar en footer.
4. Añadir CSP mínima y `Permissions-Policy`.
5. Crear pruebas unitarias para middleware de inactividad (mock de timestamps).

---

## 2025-08-20
**Contexto:** Corrección de inconsistencia en regla de negocio: impedir eventos con fecha en el pasado tanto en creación como en edición. Reporte de comportamiento errático del frontend y posibilidad de guardar fechas pasadas al editar.

**Cambios Clave:**
- `apps/eventos/models.py`: Eliminado default rígido `2025-08-06` por `timezone.now` dinámico; validación de fecha pasada ahora se aplica siempre (quitada condición `if not self.pk`).
- `apps/eventos/views.py`: Validación explícita en endpoints POST y PUT con código de error `past_date_not_allowed` para respuesta JSON consistente.
- `templates/eventos/eventos.html`: Validación JS de fecha en pasado extendida también a edición (antes solo creación).
- Pruebas: Añadido `apps/eventos/tests.py` con 4 tests (crear pasado->400, crear hoy->200, actualizar a pasado->400, actualizar a futuro->200) ejecutadas exitosamente.

**Decisiones:**
- Centralizar regla en modelo y redundar en API para mensajes claros (defensa en profundidad).
- Mantener mensaje unificado en español para consistencia UX/API.
- Añadir código de error para soporte futuro a clientes externos.

**Riesgos / Observaciones:**
- Cambio de default en modelo requiere migración para reflejar nuevo default a nivel DB (pendiente generar). No bloquea funcionamiento pero recomendable para coherencia de esquemas.
- Eventos existentes con fecha pasada siguen permitidos (correcto históricamente) — no se fuerza migración retroactiva.

**Próximos Pasos Sugeridos:**
1. Generar y aplicar migración por cambio de default `fecha_evento`.
2. Actualizar `CHANGELOG.md` (Unreleased) con fix de validación de fechas.
3. Considerar restricción adicional: prohibir mover evento confirmado a fecha anterior a hoy (ya cubierto por regla general, validar escenarios edge con TZ).
4. Revisar TZ: asegurar `USE_TZ=True` y documentación para usuarios en zonas diferentes (normalización al día actual del servidor).
5. Añadir prueba para intento de editar solo evidencias (parcial) sin afectar validación de fecha.

---
