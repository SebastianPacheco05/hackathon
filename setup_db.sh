#!/usr/bin/env bash
set -euo pipefail

# Wrapper para crear toda la base de datos (tablas, funciones, triggers, vistas).
# Uso:
#   ./setup_db.sh
#   ./setup_db.sh USER HOST DB
#   ./setup_db.sh USER HOST DB PORT
#
# Reenvía argumentos al script principal: db/apply_all.sh

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
APPLY_SCRIPT="$SCRIPT_DIR/db/apply_all.sh"
BACKEND_DIR="$SCRIPT_DIR/backend"

if [[ ! -f "$APPLY_SCRIPT" ]]; then
  echo "No se encontró $APPLY_SCRIPT"
  exit 1
fi

if ! command -v psql >/dev/null 2>&1; then
  echo "psql no está instalado o no está en PATH."
  echo "Instala PostgreSQL client y vuelve a intentar."
  exit 1
fi

chmod +x "$APPLY_SCRIPT" || true
"$APPLY_SCRIPT" "$@"

echo ""
echo "Configurando usuario administrador por defecto..."

# Resolver conexión (misma lógica base que apply_all.sh)
if [[ -n "${3:-}" ]]; then
  PGUSER="$1"
  PGHOST="$2"
  PGDATABASE="$3"
  PGPORT="${4:-5432}"
elif [[ -n "${DATABASE_URL:-}" ]]; then
  if [[ "$DATABASE_URL" =~ postgresql://([^:]+):([^@]+)@([^:]+):([0-9]+)/(.+) ]]; then
    PGUSER="${BASH_REMATCH[1]}"
    PGPASSWORD="${BASH_REMATCH[2]}"
    PGHOST="${BASH_REMATCH[3]}"
    PGPORT="${BASH_REMATCH[4]}"
    PGDATABASE="${BASH_REMATCH[5]}"
  fi
elif [[ -f "$BACKEND_DIR/.env" ]]; then
  set -a
  source "$BACKEND_DIR/.env"
  set +a
  if [[ -n "${DATABASE_URL:-}" && "$DATABASE_URL" =~ postgresql://([^:]+):([^@]+)@([^:]+):([0-9]+)/(.+) ]]; then
    PGUSER="${BASH_REMATCH[1]}"
    PGPASSWORD="${BASH_REMATCH[2]}"
    PGHOST="${BASH_REMATCH[3]}"
    PGPORT="${BASH_REMATCH[4]}"
    PGDATABASE="${BASH_REMATCH[5]}"
  fi
fi

PGUSER="${PGUSER:-revital_admin}"
PGHOST="${PGHOST:-127.0.0.1}"
PGDATABASE="${PGDATABASE:-revital_ecommerce}"
PGPORT="${PGPORT:-5432}"

# Generar hash Argon2 de la contraseña admin (compatibilidad con backend actual)
ADMIN_HASH="$("$BACKEND_DIR/venv/bin/python" - <<'PY'
from pwdlib import PasswordHash
print(PasswordHash.recommended().hash("A1ej@ndro03*"))
PY
)"

psql -v ON_ERROR_STOP=1 -h "$PGHOST" -p "$PGPORT" -U "$PGUSER" -d "$PGDATABASE" \
  -c "INSERT INTO tab_roles (id_rol, nom_rol, des_rol, usr_insert, fec_insert)
      VALUES (1, 'admin', 'Administrador del sistema', 1, NOW())
      ON CONFLICT (id_rol) DO UPDATE
      SET nom_rol = EXCLUDED.nom_rol,
          des_rol = EXCLUDED.des_rol,
          usr_update = 1,
          fec_update = NOW();" \
  -c "WITH next_id AS (
        SELECT COALESCE(MAX(id_usuario), 0) + 1 AS id
        FROM tab_usuarios
      )
      INSERT INTO tab_usuarios (
        id_usuario, nom_usuario, ape_usuario, email_usuario, password_usuario,
        id_rol, ind_genero, cel_usuario, ind_activo, usr_insert, fec_insert
      )
      VALUES (
        (SELECT id FROM next_id), 'Alejandro', 'Hernandez',
        'ahernandezlara03@gmail.com', '$ADMIN_HASH',
        1, TRUE, '3000000000', TRUE, 1, NOW()
      )
      ON CONFLICT (email_usuario) DO UPDATE
      SET password_usuario = EXCLUDED.password_usuario,
          id_rol = 1,
          ind_activo = TRUE,
          usr_update = 1,
          fec_update = NOW();"

echo "Usuario admin configurado: ahernandezlara03@gmail.com"
