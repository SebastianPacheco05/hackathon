from decimal import Decimal
from sqlalchemy.orm import Session
from sqlalchemy import text

from schemas.category_schema import CategoryCreate, CategoryUpdate
from core.config import settings
from services import mock_data_service

"""
En este archivo se crean las funciones utilizando "query by example" para interactuar con la base de datos en un CRUD básico:
 
# `get_categories`: Obtiene todos los proveedores registrados en la base de datos. (trae lo importante, no lo de auditoría)
# `get_category`: Obtiene un proveedor específico por su ID.
# `create_category`: Crea una nueva categoría en la base de datos llamando a la función fun_insert_categoria().
# `update_category`: Actualiza una categoría existente en la base de datos llamando a la función fun_update_categoria().
# `delete_category`: Elimina una categoría existente en la base de datos llamando a la función fun_delete_categoria().

Responsabilidades principales:
- consulta de árbol de categorías (raíz/línea/sublínea),
- CRUD de categorías vía funciones SQL,
- asignación de atributos por categoría (`tab_category_attributes`),
- activación/desactivación en cascada.
"""


# Todas las categorías (tab_categorias + conteo de productos activos en tab_productos)
def get_categories(db: Session):
    """
    Lista todas las categorías con conteo de productos activos.

    Se consume desde:
    - `category_router.get_categories`
    """
    if settings.MOCK_MODE:
        return mock_data_service.get_categories()
    try:
        query = text("""
        SELECT
            c.id_categoria        AS id,
            c.nom_categoria       AS name,
            c.slug_categoria      AS slug,
            c.id_categoria_padre  AS parent_id,
            c.ind_activo          AS is_active,
            c.ind_activo,
            c.usr_insert,
            c.fec_insert,
            c.usr_update,
            c.fec_update,
            (SELECT COUNT(*) FROM tab_productos p
             WHERE p.id_categoria = c.id_categoria AND p.ind_activo = true)::int AS productos_count
        FROM tab_categorias c
        """)
        result = db.execute(query)
        return result.mappings().all()
    except Exception as e:
        db.rollback()
        raise Exception(f"Error al obtener categorías: {str(e)}")

# Categorías raíz (parent_id IS NULL)
def get_categories_roots(db: Session):
    """Obtiene categorías raíz (`parent_id IS NULL`)."""
    try:
        query = text("""
        SELECT
            c.id_categoria        AS id,
            c.nom_categoria       AS name,
            c.slug_categoria      AS slug,
            c.id_categoria_padre  AS parent_id,
            c.ind_activo          AS is_active,
            c.ind_activo,
            c.usr_insert,
            c.fec_insert,
            c.usr_update,
            c.fec_update,
            (SELECT COUNT(*) FROM tab_productos p
             WHERE p.id_categoria = c.id_categoria AND p.ind_activo = true)::int AS productos_count
        FROM tab_categorias c
        WHERE c.id_categoria_padre IS NULL
        ORDER BY c.nom_categoria
        """)
        result = db.execute(query)
        return result.mappings().all()
    except Exception as e:
        db.rollback()
        raise Exception(f"Error al obtener categorías raíz: {str(e)}")

# Líneas (hijas de categorías raíz)
def get_categories_lines(db: Session):
    """Obtiene categorías de segundo nivel (líneas)."""
    try:
        query = text("""
        SELECT
            c.id_categoria        AS id,
            c.nom_categoria       AS name,
            c.slug_categoria      AS slug,
            c.id_categoria_padre  AS parent_id,
            c.ind_activo          AS is_active,
            c.ind_activo,
            c.usr_insert,
            c.fec_insert,
            c.usr_update,
            c.fec_update,
            (SELECT COUNT(*) FROM tab_productos p
             WHERE p.id_categoria = c.id_categoria AND p.ind_activo = true)::int AS productos_count
        FROM tab_categorias c
        WHERE c.id_categoria_padre IN (SELECT id_categoria FROM tab_categorias WHERE id_categoria_padre IS NULL)
        ORDER BY c.nom_categoria
        """)
        result = db.execute(query)
        return result.mappings().all()
    except Exception as e:
        db.rollback()
        raise Exception(f"Error al obtener líneas: {str(e)}")

# Sublíneas (nietas de categorías raíz)
def get_categories_sublines(db: Session):
    """Obtiene categorías de tercer nivel (sublíneas)."""
    try:
        query = text("""
        SELECT
            c.id_categoria        AS id,
            c.nom_categoria       AS name,
            c.slug_categoria      AS slug,
            c.id_categoria_padre  AS parent_id,
            c.ind_activo          AS is_active,
            c.ind_activo,
            c.usr_insert,
            c.fec_insert,
            c.usr_update,
            c.fec_update,
            (SELECT COUNT(*) FROM tab_productos p
             WHERE p.id_categoria = c.id_categoria AND p.ind_activo = true)::int AS productos_count
        FROM tab_categorias c
        WHERE c.id_categoria_padre IN (
            SELECT id_categoria FROM tab_categorias
            WHERE id_categoria_padre IN (SELECT id_categoria FROM tab_categorias WHERE id_categoria_padre IS NULL)
        )
        ORDER BY c.nom_categoria
        """)
        result = db.execute(query)
        return result.mappings().all()
    except Exception as e:
        db.rollback()
        raise Exception(f"Error al obtener sublíneas: {str(e)}")

# Una categoría específica (tab_categorias)
def get_category(db: Session, category_id: Decimal):
    """Obtiene una categoría por ID con su conteo de productos activos."""
    if settings.MOCK_MODE:
        return mock_data_service.get_category_by_id(int(category_id))
    try:
        query = text("""
        SELECT
            c.id_categoria        AS id,
            c.nom_categoria       AS name,
            c.slug_categoria      AS slug,
            c.id_categoria_padre  AS parent_id,
            c.ind_activo          AS is_active,
            c.ind_activo,
            c.usr_insert,
            c.fec_insert,
            c.usr_update,
            c.fec_update,
            (SELECT COUNT(*) FROM tab_productos p
             WHERE p.id_categoria = c.id_categoria AND p.ind_activo = true)::int AS productos_count
        FROM tab_categorias c
        WHERE c.id_categoria = :category_id
        """)
        result = db.execute(query, {"category_id": category_id})
        return result.mappings().first()
    except Exception as e:
        db.rollback()
        raise Exception(f"Error al obtener la categoría: {str(e)}")
    
    
# Crear una categoría (fun_insert_categoria: p_name, p_parent_id, p_is_active, p_usr_operacion)
def create_category(db: Session, category: CategoryCreate, usr_insert: Decimal):
    """
    Crea categoría mediante `fun_insert_categoria`.

    Comportamiento:
    - acepta `is_active` o `ind_activo` desde frontend,
    - parsea mensaje SQL para extraer `id` creado cuando aplica.
    """
    if settings.MOCK_MODE:
        return Decimal(str(mock_data_service.create_category(category.model_dump(exclude_none=True))))
    try:
        payload = category.model_dump(exclude_none=True)
        query = text("""
        SELECT fun_insert_categoria(
            :p_name,
            :p_parent_id,
            :p_is_active,
            :p_usr_operacion
        )
        """)
        # Aceptar is_active o ind_activo del frontend; por defecto True al crear
        is_active = payload.get("is_active") if payload.get("is_active") is not None else payload.get("ind_activo", True)
        result = db.execute(query, {
            "p_name": payload.get("name"),
            "p_parent_id": payload.get("parent_id"),
            "p_is_active": is_active,
            "p_usr_operacion": usr_insert,
        })
        fetched_result = result.fetchone()
        db.commit()
        msg = fetched_result[0] if fetched_result else None
        if not msg:
            return None
        msg_str = str(msg).strip()
        if msg_str.upper().startswith("ERROR"):
            raise Exception(msg_str)
        # Mensaje de éxito: "Categoría insertada correctamente. Id: 123"
        prefix = "Categoría insertada correctamente. Id:"
        if prefix in msg_str:
            id_str = msg_str.split(prefix, 1)[-1].strip()
            return Decimal(id_str) if id_str.isdigit() else None
        return None
    except Exception as e:
        db.rollback()
        raise Exception(f"Error al crear la categoría: {str(e)}")
    
# Actualizar categoría (fun_update_categoria: p_id, p_name, p_parent_id, p_is_active, p_usr_operacion)
def update_category(db: Session, category_id: Decimal, category: CategoryUpdate, usr_update: Decimal):
    """
    Actualiza categoría mediante `fun_update_categoria`.

    Nota:
    - si faltan campos opcionales, usa valores actuales para mantener contrato.
    """
    if settings.MOCK_MODE:
        return mock_data_service.update_category(int(category_id), category.model_dump(exclude_unset=True))
    try:
        payload = category.model_dump(exclude_unset=True)
        # Obtener valores actuales si no se envían (la función espera p_name obligatorio)
        current = get_category(db, category_id)
        if not current:
            raise ValueError("Categoría no encontrada")
        name = payload.get("name", current.get("name"))
        query = text("""
        SELECT fun_update_categoria(
            :p_id,
            :p_name,
            :p_parent_id,
            :p_is_active,
            :p_usr_operacion
        )
        """)
        is_active = payload.get("is_active") if payload.get("is_active") is not None else payload.get("ind_activo")
        if is_active is None:
            is_active = current.get("is_active", True)
        result = db.execute(query, {
            "p_id": category_id,
            "p_name": name,
            "p_parent_id": payload.get("parent_id"),
            "p_is_active": is_active,
            "p_usr_operacion": usr_update,
        })
        fetched_result = result.fetchone()
        db.commit()
        return fetched_result[0] if fetched_result else None
    except Exception as e:
        db.rollback()
        raise Exception(f"Error al actualizar la categoría: {str(e)}")

# Activar o desactivar categoría (fun_deactivate_activate_categoria: p_id_categoria, p_activar, p_usr_operacion)
def deactivate_activate_category(db: Session, category_id: Decimal, usr_update: Decimal, activar: bool):
    """
    Activa o desactiva una categoría y en cascada subcategorías y productos (tab_categories / tab_products).

    Implementación:
    - delega en `fun_deactivate_activate_categoria`.
    """
    if settings.MOCK_MODE:
        return mock_data_service.toggle_category(int(category_id), bool(activar))
    try:
        query = text("""
        SELECT fun_deactivate_activate_categoria(:p_id_categoria, :p_activar, :p_usr_operacion)
        """)
        result = db.execute(query, {
            "p_id_categoria": category_id,
            "p_activar": activar,
            "p_usr_operacion": usr_update,
        })
        fetched_result = result.fetchone()
        db.commit()
        return fetched_result[0] if fetched_result else None
    except Exception as e:
        db.rollback()
        raise Exception(f"Error al cambiar estado de la categoría: {str(e)}")

#Desactivar una categoria (mantener compatibilidad)
def deactivate_category(db: Session, category_id: Decimal, usr_update: Decimal):
    """
    Desactiva una categoría (wrapper para mantener compatibilidad).
    """
    return deactivate_activate_category(db, category_id, usr_update, False)


def get_category_attributes(db: Session, category_id: Decimal):
    """
    Lista atributos de una categoría (tab_category_attributes + nombre y data_type del atributo).
    Returns list of dicts: id, category_id, attribute_id, is_required, is_filterable, attribute_name, data_type.

    Se usa en:
    - configuración de formulario de producto por categoría.
    """
    if settings.MOCK_MODE:
        return mock_data_service.get_category_attributes(int(category_id))
    try:
        query = text("""
            SELECT
                ca.id_atributo_categoria    AS id,
                ca.id_categoria             AS category_id,
                ca.id_atributo              AS attribute_id,
                ca.ind_obligatorio          AS is_required,
                ca.ind_filtrable            AS is_filterable,
                a.nom_atributo              AS attribute_name,
                a.tipo_dato                 AS data_type,
                COALESCE(a.ind_valores_predefinidos, FALSE) AS has_predefined_values
            FROM tab_atributos_categoria ca
            JOIN tab_atributos a ON a.id_atributo = ca.id_atributo
            WHERE ca.id_categoria = :category_id
            ORDER BY a.nom_atributo
        """)
        result = db.execute(query, {"category_id": category_id})
        return result.mappings().all()
    except Exception as e:
        db.rollback()
        raise Exception(f"Error al obtener atributos de la categoría: {str(e)}")


def get_category_attributes_with_values(db: Session, category_id: Decimal):
    """
    Lista atributos de la categoría con sus valores predefinidos (cuando has_predefined_values=True).
    Una sola query de atributos y una de valores para evitar N+1.

    Resultado:
    - lista de atributos, cada uno con `values` listo para UI.
    """
    if settings.MOCK_MODE:
        rows = mock_data_service.get_category_attributes(int(category_id))
        return [{**dict(r), "values": []} for r in rows]
    try:
        attrs = get_category_attributes(db, category_id)
        attrs = [dict(a) for a in attrs]
        ids_with_values = [a["attribute_id"] for a in attrs if a.get("has_predefined_values")]
        if not ids_with_values:
            return [{"values": [], **a} for a in attrs]
        placeholders = ", ".join(f":id{i}" for i in range(len(ids_with_values)))
        values_q = text(f"""
            SELECT id_valor_atributo AS id, id_atributo AS attribute_id,
                   valor AS value, color_hex AS hex_color, orden AS sort_order
            FROM tab_valores_atributo
            WHERE id_atributo IN ({placeholders}) AND ind_activo = TRUE
            ORDER BY id_atributo, orden, id_valor_atributo
        """)
        params = {f"id{i}": aid for i, aid in enumerate(ids_with_values)}
        values_rows = db.execute(values_q, params).mappings().all()
        by_attr: dict = {}
        for row in values_rows:
            aid = row["attribute_id"]
            if aid not in by_attr:
                by_attr[aid] = []
            by_attr[aid].append({"id": row["id"], "value": row["value"], "hex_color": row["hex_color"], "sort_order": row["sort_order"]})
        for a in attrs:
            a["values"] = by_attr.get(a["attribute_id"], [])
        return attrs
    except Exception as e:
        db.rollback()
        raise Exception(f"Error al obtener atributos con valores: {str(e)}")


def set_category_attributes(db: Session, category_id: Decimal, items: list, usr: Decimal):
    """
    Reemplaza los atributos de una categoría: borra los existentes e inserta los nuevos.
    items: list of dicts with keys attribute_id, is_required, is_filterable.
    UNIQUE(category_id, attribute_id) respetado; id generado con COALESCE(MAX(id),0)+row_number.

    Estrategia:
    - operación de reemplazo total para simplificar sincronización frontend-backend.
    """
    if settings.MOCK_MODE:
        mock_data_service.set_category_attributes(int(category_id), items)
        return
    try:
        delete_q = text("DELETE FROM tab_atributos_categoria WHERE id_categoria = :category_id")
        db.execute(delete_q, {"category_id": category_id})
        if not items:
            db.commit()
            return
        # Obtener siguiente id (evitar conflicto con múltiples inserts)
        max_q = text("SELECT COALESCE(MAX(id_atributo_categoria), 0) AS mx FROM tab_atributos_categoria")
        row = db.execute(max_q).fetchone()
        next_id = int(row[0]) + 1 if row else 1
        insert_q = text("""
            INSERT INTO tab_atributos_categoria
                (id_atributo_categoria, id_categoria, id_atributo, ind_obligatorio, ind_filtrable, usr_insert)
            VALUES (:id, :category_id, :attribute_id, :is_required, :is_filterable, :usr_insert)
        """)
        for i, item in enumerate(items):
            db.execute(insert_q, {
                "id": next_id + i,
                "category_id": category_id,
                "attribute_id": item["attribute_id"],
                "is_required": item.get("is_required", False),
                "is_filterable": item.get("is_filterable", False),
                "usr_insert": usr,
            })
        db.commit()
    except Exception as e:
        db.rollback()
        raise Exception(f"Error al guardar atributos de la categoría: {str(e)}")
