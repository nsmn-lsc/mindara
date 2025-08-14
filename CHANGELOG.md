# Changelog

Formato basado en Keep a Changelog y Semantic Versioning.

## [Unreleased]
### Added
- (pendiente)

### Changed
- (pendiente)

### Fixed
- (pendiente)

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
