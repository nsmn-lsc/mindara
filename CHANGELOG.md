# Changelog

Formato basado en Keep a Changelog y Semantic Versioning.

## [Unreleased]
### Added
- Pruebas automatizadas para validación de fechas de eventos (creación y edición).

### Changed
- Validación de fecha de evento movida a aplicar tanto en creación como en edición (regla centralizada en modelo + refuerzo en API).
- Default de `Evento.fecha_evento` ahora dinámico (`timezone.now`) en lugar de fecha fija.
- Limpieza automática de mensajes/estilos de error al reabrir/cerrar el modal de eventos para evitar confusión del usuario.

### Fixed
- Se impedía (intermitentemente) interpretar que eventos futuros estaban bloqueados tras un intento fallido: ahora el modal se limpia correctamente.
- Posibilidad de guardar un evento editado con fecha en el pasado (PUT) — ahora rechazado con código `past_date_not_allowed`.
- Inconsistencia: creación impedía pasado pero edición lo permitía; corregido.

## [0.2.0] - 2025-08-14
### Added
- Página de Términos y Licencia (Apache-2.0) enlazada en el footer.
- Archivo LICENSE (Apache-2.0) y NOTICE con créditos y traducción introductoria en español.

### Changed
- Normalización completa de estructura de assets estáticos (`static/` versionado, `staticfiles/` solo como destino collectstatic).
- Footer actualizado (enlaces: Ayuda, Términos, placeholder Privacidad).

### Fixed
- 404 potenciales de FullCalendar por directorio sin versionar.

### Security
- Configuración lista para activar `CompressedManifestStaticFilesStorage` (aún con fallback simple temporal en producción).

[Unreleased]: https://github.com/nsmn-lsc/mindara/compare/v0.2.0...HEAD
[0.2.0]: https://github.com/nsmn-lsc/mindara/releases/tag/v0.2.0
