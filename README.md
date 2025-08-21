# Mindara

Proyecto Django

## � Características principales

- Django 5 + PostgreSQL
- Usuario personalizado con roles (ADMIN / MANAGER / USER)
- Gestión de eventos (prioridad, duración, etapa)
- Página de estadísticas de eventos por usuario con:
	- Filtros (nombre, prioridad, rango fechas, usuario)
	- Paginación y exportación CSV
	- Gráfica dinámica (mes actual, últimos 3 y 12 meses) con agregaciones ORM
- WhiteNoise para servir estáticos en producción
- Health check en `/healthz` para plataformas (Render)

---

## �🚀 Inicio rápido

```bash
# Iniciar servidor
./dev.sh runserver

# Ver comandos disponibles
./dev.sh help
```

## 🌐 URLs

- **Desarrollo**: http://127.0.0.1:8000/
- **Admin**: http://127.0.0.1:8000/admin/ (admin/admin123)

## 📁 Estructura

```
Mindara/
├── manage.py              # Comando principal Django
├── dev.sh                 # Script de desarrollo
├── core/                  # Configuración del proyecto
├── apps/                  # Aplicaciones Django
├── static/                # Archivos estáticos
├── media/                 # Archivos subidos
├── templates/             # Templates HTML
└── .env                   # Variables de entorno
```

## 🛠️ Comandos útiles

```bash
./dev.sh runserver        # Iniciar servidor
./dev.sh migrate          # Aplicar migraciones
./dev.sh makemigrations   # Crear migraciones
./dev.sh shell            # Shell Django
./dev.sh createsuperuser  # Crear admin
./dev.sh test             # Ejecutar tests
./dev.sh check            # Verificar proyecto
```

## 📊 Base de datos

- **Motor local recomendado**: PostgreSQL
- Puedes usar SQLite para pruebas rápidas (valor por defecto), pero producción usa Postgres.

### 🔧 Configuración PostgreSQL local

1. Crear base de datos y usuario:
```sql
CREATE DATABASE mindara;
CREATE USER mindara_user WITH PASSWORD 'cambia_esto';
ALTER ROLE mindara_user SET client_encoding TO 'utf8';
ALTER ROLE mindara_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE mindara_user SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE mindara TO mindara_user;
```
2. Archivo `.env` (ejemplo):
```
SECRET_KEY=pon_uno_seguro
DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost
DB_ENGINE=django.db.backends.postgresql
DB_NAME=mindara
DB_USER=mindara_user
DB_PASSWORD=cambia_esto
DB_HOST=127.0.0.1
DB_PORT=5432
```
3. Migraciones y superusuario:
```bash
python manage.py migrate
python manage.py createsuperuser
```

---

## 🌱 Variables de entorno clave

| Variable | Descripción |
|----------|-------------|
| SECRET_KEY | Clave secreta Django |
| DEBUG | True / False |
| ALLOWED_HOSTS | Lista separada por comas |
| DB_ENGINE | Motor (postgresql / sqlite3) |
| DB_NAME / USER / PASSWORD / HOST / PORT | Credenciales BD |
| DATABASE_URL | (Opcional) URI completa (Render) |

Si `DATABASE_URL` está presente tiene prioridad (usa `dj-database-url`).

---

## 🚀 Despliegue en Render (Free tier inicial)

Incluye `render.yaml` y `Procfile`.

### Pasos
1. Subir el repositorio a GitHub/GitLab.
2. Conectar servicio en Render → New + Blueprint → seleccionar repo.
3. Render detectará `render.yaml` y creará:
	- Servicio web (plan free)
	- Base de datos PostgreSQL (free)
4. Variables generadas automáticamente (SECRET_KEY se puede regenerar).
5. Primer build ejecuta:
	- Instalación dependencias (`requirements.txt`)
	- `collectstatic`
	- `migrate`
6. Health check disponible: `https://<tu-dominio>/healthz`

### Notas producción
| Área | Acción |
|------|--------|
| Estáticos | WhiteNoise ya configurado |
| Seguridad | HSTS + SSL redirect cuando DEBUG=False |
| Logs | Gunicorn envía a stdout (Render los captura) |
| Scaling | Aumentar workers o plan cuando >100 req concurrentes |
| DB | Migrar a plan de pago para mayor almacenamiento cuando haga falta |

---

## 📈 Página de estadísticas
Ruta: `/dashboard/eventos-usuarios/`

Incluye:
- Tabla por usuario (total, activos, completados, urgentes, último evento)
- Gráfica con modos: `chart=mes | 3m | 12m`
- Export CSV: parámetro `export=csv`

### Agregaciones ORM usadas
- `Count` condicional (mes, urgentes)
- Subquery para último evento (fecha/hora/nombre)
- Cálculo completados vs activos con expresión SQL (PostgreSQL)

Para compatibilidad SQLite (si se necesitara) reemplazar la expresión RawSQL por un cálculo Python.

---

## 🧪 Tests (sugerido)
Ejecutar:
```bash
pytest
```
Agregar tests para vista de estadísticas (respuesta 200, claves contexto, export CSV).

---

## 🔐 Recomendaciones posteriores
1. Añadir Sentry / monitoreo.
2. Limitar ALLOWED_HOSTS en producción.
3. Configurar rotación de logs (si se pasa a contenedor persistente).
4. Cache ligera (Redis) para `chart_json` si crece el volumen.
5. Índices adicionales si aumentan filtros complejos.

---

## 🗺 Roadmap corto
- Stacked bars (activos vs completados) modo “mes”.
- Export XLSX.
- Filtros por etapa / categoría.
- Panel de reportes descargables.

## 🎯 Próximos pasos

1. Crear apps en `apps/`
2. Configurar URLs
3. Desarrollar modelos
4. Crear vistas y templates
5. Ajustar métricas y monitoreo en producción

---

© Mindara
