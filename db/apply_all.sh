#!/usr/bin/env bash
#
# Script para crear toda la base de datos Revital e-commerce desde cero (idempotente).
# Aplica en orden: 1) schema, 2) funciones, 3) triggers, 4) vistas, 5) KPIs opcionales.
#
# Uso:
#   ./apply_all.sh
#   ./apply_all.sh USER HOST DB
#   ./apply_all.sh USER HOST DB PORT
#
# Sin argumentos, usa variables de entorno (PGHOST, PGPORT, PGUSER, PGDATABASE)
# o carga backend/.env automáticamente (incluyendo DATABASE_URL).
#
# IMPORTANTE: PGUSER debe ser el dueño de la DB (p. ej. postgres o revital_admin)
# para poder crear/reemplazar funciones.
# Ejemplo: ./apply_all.sh postgres 46.225.94.64 revital_ecommerce 5432
#
set -e
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# --- Cargar .env del backend si no hay argumentos ---
if [[ $# -eq 0 && -z "$DATABASE_URL" && -f "$SCRIPT_DIR/../backend/.env" ]]; then
    set -a
    source "$SCRIPT_DIR/../backend/.env"
    set +a
fi

# --- Conexión ---
if [[ -n "${3:-}" ]]; then
    export PGUSER="$1"
    export PGHOST="$2"
    export PGDATABASE="$3"
    export PGPORT="${4:-5432}"
elif [[ -n "$DATABASE_URL" ]]; then
    if [[ "$DATABASE_URL" =~ postgresql://([^:]+):([^@]+)@([^:]+):([0-9]+)/(.+) ]]; then
        export PGUSER="${BASH_REMATCH[1]}"
        export PGPASSWORD="${BASH_REMATCH[2]}"
        export PGHOST="${BASH_REMATCH[3]}"
        export PGPORT="${BASH_REMATCH[4]}"
        export PGDATABASE="${BASH_REMATCH[5]}"
    fi
fi
PGUSER="${PGUSER:-revital_admin}"
PGHOST="${PGHOST:-127.0.0.1}"
PGDATABASE="${PGDATABASE:-revital_ecommerce}"
PGPORT="${PGPORT:-5432}"

echo "=============================================="
echo "Revital e-commerce – Aplicar schema y objetos"
echo "=============================================="
echo "Host: $PGHOST:$PGPORT | DB: $PGDATABASE | User: $PGUSER"
echo ""

run_psql() {
    psql -v ON_ERROR_STOP=1 -h "$PGHOST" -p "$PGPORT" -U "$PGUSER" -d "$PGDATABASE" -f "$1"
}

# --- 1. Schema (tablas) ---
echo "[1/5] Aplicando schema (db_revital.sql)..."
run_psql "$SCRIPT_DIR/db_revital.sql"
echo ""

# --- 1.5. Migraciones idempotentes ---
if [[ -f "$SCRIPT_DIR/migrations/add_opciones_elegidas_orden_productos.sql" ]]; then
    echo "[1.5] Migración: add_opciones_elegidas_orden_productos.sql"
    run_psql "$SCRIPT_DIR/migrations/add_opciones_elegidas_orden_productos.sql" || true
    echo ""
fi

# --- 2. Funciones ---
echo "[2/5] Aplicando funciones..."

# Eliminar funciones fun_* previas para evitar conflictos de firma al recrear.
psql -v ON_ERROR_STOP=1 -h "$PGHOST" -p "$PGPORT" -U "$PGUSER" -d "$PGDATABASE" -c "
DO \$\$
DECLARE r RECORD;
BEGIN
  FOR r IN
    SELECT n.nspname AS schema_name,
           p.proname AS function_name,
           pg_get_function_identity_arguments(p.oid) AS args
    FROM pg_proc p
    JOIN pg_namespace n ON n.oid = p.pronamespace
    WHERE n.nspname = 'public' AND p.proname LIKE 'fun_%'
  LOOP
    EXECUTE format('DROP FUNCTION IF EXISTS %I.%I(%s) CASCADE',
                   r.schema_name, r.function_name, r.args);
  END LOOP;
END
\$\$;
"

# 2.1 Utils (slug, sku) – primero porque otros dependen de ellas
for f in "$SCRIPT_DIR/Functions/utils"/fun_*.sql; do
    [[ -f "$f" ]] || continue
    echo "  - utils/$(basename "$f")"
    run_psql "$f"
done

# 2.2 Categorías (dependen de utils)
for f in "$SCRIPT_DIR/Functions/tab_categorias"/fun_*.sql; do
    [[ -f "$f" ]] || continue
    echo "  - tab_categorias/$(basename "$f")"
    run_psql "$f"
done

# 2.3 Productos (dependen de utils y categorías)
for f in "$SCRIPT_DIR/Functions/tab_productos"/fun_*.sql; do
    [[ -f "$f" ]] || continue
    echo "  - tab_productos/$(basename "$f")"
    run_psql "$f"
done
if [[ -f "$SCRIPT_DIR/Functions/tab_productos/indexes_filter_products.sql" ]]; then
    echo "  - tab_productos/indexes_filter_products.sql"
    run_psql "$SCRIPT_DIR/Functions/tab_productos/indexes_filter_products.sql" || true
fi

# 2.4 Resto de funciones (todos los directorios restantes)
# Omitimos directorios legacy que referencian tablas eliminadas del schema actual.
for dir in "$SCRIPT_DIR/Functions"/tab_*; do
    [[ -d "$dir" ]] || continue
    case "$(basename "$dir")" in
        tab_categorias|tab_productos|tab_kpis_dashboards|tab_lineas|tab_sublineas) continue ;;
    esac
    for f in "$dir"/*.sql; do
        [[ -f "$f" ]] || continue
        base="$(basename "$f")"
        [[ "$base" == EJEMPLOS* ]] && continue
        [[ "$base" == *unificada*.sql ]] && continue
        echo "  - $(basename "$dir")/$base"
        run_psql "$f"
    done
done
echo ""

# --- 3. Triggers ---
echo "[3/5] Aplicando triggers..."
for f in \
    "$SCRIPT_DIR/triggers/audit.sql" \
    "$SCRIPT_DIR/triggers/trg_actualizar_estadisticas_ventas.sql" \
    "$SCRIPT_DIR/triggers/trg_actualizar_stock_compra_proveedor.sql" \
    "$SCRIPT_DIR/triggers/trg_acumular_puntos_orden.sql" \
    "$SCRIPT_DIR/triggers/trg_automatizar_pagos_descuentos.sql" \
    "$SCRIPT_DIR/triggers/trg_actualizar_stock_orden_pagada.sql" \
    "$SCRIPT_DIR/triggers/triggers.sql"; do
    [[ -f "$f" ]] || continue
    echo "  - $(basename "$f")"
    run_psql "$f"
done
echo ""

# --- 4. Vistas ---
echo "[4/5] Aplicando vistas..."
for f in "$SCRIPT_DIR/views"/*.sql; do
    [[ -f "$f" ]] || continue
    echo "  - $(basename "$f")"
    run_psql "$f"
done
echo ""

# --- 5. KPIs (opcionales) ---
echo "[5/5] Objetos opcionales (KPIs)..."
KPI_DIR="$SCRIPT_DIR/Functions/tab_kpis_dashboards"

if [[ -f "$KPI_DIR/schema_kpis_personalizados.sql" ]]; then
    echo "  - schema_kpis_personalizados.sql"
    run_psql "$KPI_DIR/schema_kpis_personalizados.sql"
fi

for f in "$KPI_DIR"/fun_*.sql; do
    [[ -f "$f" ]] || continue
    echo "  - $(basename "$f")"
    run_psql "$f"
done

if [[ -f "$KPI_DIR/vistas_kpis_sistema.sql" ]]; then
    echo "  - vistas_kpis_sistema.sql"
    run_psql "$KPI_DIR/vistas_kpis_sistema.sql"
fi

if [[ -f "$KPI_DIR/datos_kpis_iniciales.sql" ]]; then
    KPI_COUNT="$(psql -tA -h "$PGHOST" -p "$PGPORT" -U "$PGUSER" -d "$PGDATABASE" \
        -c "SELECT COUNT(1) FROM tab_kpis_maestros;" 2>/dev/null || echo "0")"
    if [[ "${KPI_COUNT:-0}" -gt 0 ]]; then
        echo "  - datos_kpis_iniciales.sql [SKIP: ya existen datos]"
    else
        echo "  - datos_kpis_iniciales.sql"
        run_psql "$KPI_DIR/datos_kpis_iniciales.sql"
    fi
fi
echo ""

echo "=============================================="
echo "Proceso terminado."
echo "=============================================="
