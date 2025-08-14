#!/usr/bin/env bash
# Actualiza la sección [Unreleased] del CHANGELOG con categorías vacías si faltan.
# Uso: ./scripts/maintenance/update_log.sh "Mensaje corto" "Categoria" (Added|Changed|Fixed|Security|Removed)

set -euo pipefail
CHANGELOG_FILE="CHANGELOG.md"
MSG=${1:-}
CAT=${2:-Added}
DATE=$(date +%Y-%m-%d)

if [[ -z "$MSG" ]]; then
  echo "Uso: $0 'Descripción del cambio' [Added|Changed|Fixed|Security|Removed]" >&2
  exit 1
fi

# Asegura secciones básicas en [Unreleased]
ensure_section() {
  local section="$1"
  if ! grep -q "^### ${section}$" "$CHANGELOG_FILE"; then
    # Insertar antes de la primera versión (después de encabezado de [Unreleased])
    awk -v sec="${section}" '1; /^## \[0/ { if (!ins) { print "### "sec"\n- (pendiente)\n"; ins=1 } }' "$CHANGELOG_FILE" >"$CHANGELOG_FILE.tmp" && mv "$CHANGELOG_FILE.tmp" "$CHANGELOG_FILE"
  fi
}

for s in Added Changed Fixed Security Removed; do
  ensure_section "$s"
  # Quita marcador (pendiente) si se va a añadir algo en esa sección
  if [[ "$s" == "$CAT" ]]; then
    # Si la línea '- (pendiente)' está justo después del título de sección, eliminarla.
    perl -0777 -pe "s/(### $CAT\n)(- \(pendiente\)\n)/\1/" -i "$CHANGELOG_FILE"
  fi
done

# Inserta la entrada en la sección correspondiente (después del encabezado)
perl -0777 -pe "s/(### $CAT\n)/\1- $MSG\n/" -i "$CHANGELOG_FILE"

echo "Entrada añadida a [Unreleased] -> $CAT: $MSG"
