#!/bin/bash
# Script de desarrollo genérico para proyectos Django con Poetry

# Auto-detectar nombre del proyecto desde el directorio
PROJECT_NAME=$(basename "$(pwd)")
echo "🚀 $PROJECT_NAME - Entorno de desarrollo"
echo "========================================"

# Limpiar variables de entorno que puedan interferir
unset DB_ENGINE DB_NAME DB_USER DB_PASSWORD DB_HOST DB_PORT

# Auto-detectar puerto disponible
find_available_port() {
    for port in 8000 8001 8002 8003 8004 8005; do
        if ! nc -z 127.0.0.1 $port 2>/dev/null; then
            echo $port
            return
        fi
    done
    echo 8000
}

# Función para mostrar ayuda
show_help() {
    echo "Uso: $0 [comando]"
    echo ""
    echo "Comandos disponibles:"
    echo "  runserver    - Iniciar servidor de desarrollo"
    echo "  migrate      - Aplicar migraciones"
    echo "  makemigrations - Crear migraciones"
    echo "  shell        - Abrir shell de Django"
    echo "  createsuperuser - Crear superusuario"
    echo "  install      - Instalar dependencias"
    echo "  test         - Ejecutar tests"
    echo "  collectstatic - Recopilar archivos estáticos"
    echo "  check        - Verificar proyecto Django"
    echo "  help         - Mostrar esta ayuda"
    echo ""
    echo "Proyecto: $PROJECT_NAME"
}

# Verificar que existe manage.py
if [ ! -f "manage.py" ]; then
    echo "❌ Error: No se encontró manage.py"
    echo "Ejecuta primero: django-admin startproject core ."
    exit 1
fi

# Ejecutar comando
case $1 in
    "runserver")
        PORT=$(find_available_port)
        echo "📡 Iniciando servidor en puerto $PORT..."
        poetry run python manage.py runserver 127.0.0.1:$PORT
        ;;
    "migrate")
        echo "🔄 Aplicando migraciones..."
        poetry run python manage.py migrate
        ;;
    "makemigrations")
        echo "📝 Creando migraciones..."
        poetry run python manage.py makemigrations
        ;;
    "shell")
        echo "🐚 Abriendo shell de Django..."
        poetry run python manage.py shell
        ;;
    "createsuperuser")
        echo "👤 Creando superusuario..."
        poetry run python manage.py createsuperuser
        ;;
    "install")
        echo "📦 Instalando dependencias..."
        poetry install --no-root
        ;;
    "test")
        echo "🧪 Ejecutando tests..."
        poetry run python manage.py test
        ;;
    "collectstatic")
        echo "📂 Recopilando archivos estáticos..."
        poetry run python manage.py collectstatic --noinput
        ;;
    "check")
        echo "🔍 Verificando proyecto..."
        poetry run python manage.py check
        ;;
    "help"|"-h"|"--help")
        show_help
        ;;
    "")
        show_help
        ;;
    *)
        echo "❌ Comando no reconocido: $1"
        show_help
        exit 1
        ;;
esac
