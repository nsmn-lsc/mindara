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
