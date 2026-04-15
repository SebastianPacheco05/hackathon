"""
Servicio para CRUD de atributos y valores predefinidos.

Cubre:
- `tab_atributos`: definición de atributos (tipo, nombre, flags).
- `tab_valores_atributo`: valores permitidos por atributo.

Reglas principales:
- unicidad de nombres por atributo/valor,
- validación de tipo de dato,
- bloqueo de borrado cuando hay referencias activas.
"""
from decimal import Decimal
from sqlalchemy.orm import Session
from sqlalchemy import text

from schemas.attribute_schema import (
    AttributeCreate,
    AttributeUpdate,
    AttributeValueCreate,
    AttributeValueUpdate,
)

VALID_DATA_TYPES = ("text", "number", "boolean")

# Mapa: campo Pydantic → columna real en tab_atributos
_ATTR_COL_MAP = {
    "name": "nom_atributo",
    "data_type": "tipo_dato",
    "has_predefined_values": "ind_valores_predefinidos",
    "usr_update": "usr_update",
    "fec_update": "fec_update",
}

# Mapa: campo Pydantic → columna real en tab_valores_atributo
_VAL_COL_MAP = {
    "value": "valor",
    "hex_color": "color_hex",
    "sort_order": "orden",
    "is_active": "ind_activo",
    "usr_update": "usr_update",
    "fec_update": "fec_update",
}


def _table_exists(db: Session, table_name: str) -> bool:
    """Verifica si una tabla existe en el esquema actual de BD."""
    return bool(
        db.execute(
            text("SELECT to_regclass(:table_name) IS NOT NULL"),
            {"table_name": table_name},
        ).scalar()
    )


def get_all(db: Session):
    """
    Lista atributos del catálogo maestro.

    Se consume desde:
    - `attribute_router.get_attributes`
    """
    try:
        q = text("""
            SELECT id_atributo AS id, nom_atributo AS name, tipo_dato AS data_type,
                   ind_valores_predefinidos AS has_predefined_values,
                   usr_insert, fec_insert, usr_update, fec_update
            FROM tab_atributos
            ORDER BY nom_atributo
        """)
        result = db.execute(q)
        return result.mappings().all()
    except Exception as e:
        db.rollback()
        raise Exception(f"Error al obtener atributos: {str(e)}")


def get_by_id(db: Session, id_attr: Decimal):
    """Obtiene un atributo por su ID."""
    try:
        q = text("""
            SELECT id_atributo AS id, nom_atributo AS name, tipo_dato AS data_type,
                   ind_valores_predefinidos AS has_predefined_values,
                   usr_insert, fec_insert, usr_update, fec_update
            FROM tab_atributos
            WHERE id_atributo = :id
        """)
        result = db.execute(q, {"id": id_attr})
        return result.mappings().first()
    except Exception as e:
        db.rollback()
        raise Exception(f"Error al obtener atributo: {str(e)}")


def _validate_data_type(data_type: str) -> None:
    """Valida que el tipo esté dentro de los permitidos por negocio."""
    if data_type not in VALID_DATA_TYPES:
        raise ValueError(f"data_type debe ser uno de: {', '.join(VALID_DATA_TYPES)}")


def create(db: Session, attr: AttributeCreate, usr_insert: Decimal):
    """
    Crea un atributo nuevo.

    Validaciones:
    - `data_type` permitido,
    - nombre único (case-insensitive),
    - asignación manual de `id` incremental (convención actual).
    """
    try:
        _validate_data_type(attr.data_type)
        existing = db.execute(
            text("SELECT 1 FROM tab_atributos WHERE LOWER(TRIM(nom_atributo)) = LOWER(TRIM(:name))"),
            {"name": attr.name}
        ).first()
        if existing:
            raise ValueError("Ya existe un atributo con ese nombre")
        next_id = db.execute(text("SELECT COALESCE(MAX(id_atributo), 0) + 1 FROM tab_atributos")).scalar()
        db.execute(
            text("""
                INSERT INTO tab_atributos (id_atributo, nom_atributo, tipo_dato, ind_valores_predefinidos, usr_insert)
                VALUES (:id, :name, :data_type, :has_predefined_values, :usr_insert)
            """),
            {
                "id": next_id,
                "name": attr.name.strip(),
                "data_type": attr.data_type,
                "has_predefined_values": getattr(attr, "has_predefined_values", False),
                "usr_insert": usr_insert,
            }
        )
        db.commit()
        return next_id
    except ValueError:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        raise Exception(f"Error al crear atributo: {str(e)}")


def update(db: Session, id_attr: Decimal, attr: AttributeUpdate, usr_update: Decimal):
    """
    Actualiza un atributo existente.

    Validaciones:
    - atributo existe,
    - si cambia nombre, mantener unicidad,
    - si cambia tipo, validar catálogo de tipos permitidos.
    """
    try:
        current = get_by_id(db, id_attr)
        if not current:
            raise ValueError("Atributo no encontrado")
        updates = attr.model_dump(exclude_unset=True)
        if not updates:
            return
        if "data_type" in updates:
            _validate_data_type(updates["data_type"])
        if "name" in updates:
            existing = db.execute(
                text("SELECT 1 FROM tab_atributos WHERE LOWER(TRIM(nom_atributo)) = LOWER(TRIM(:name)) AND id_atributo != :id"),
                {"name": updates["name"], "id": id_attr}
            ).first()
            if existing:
                raise ValueError("Ya existe un atributo con ese nombre")
        # Traducir campos Pydantic → columnas DB
        db_updates = {_ATTR_COL_MAP.get(k, k): v for k, v in updates.items()}
        set_clause = ", ".join(f"{col} = :{col}" for col in db_updates)
        db_updates["id_atributo"] = id_attr
        db_updates["usr_update"] = usr_update
        db.execute(
            text(f"UPDATE tab_atributos SET {set_clause}, usr_update = :usr_update WHERE id_atributo = :id_atributo"),
            db_updates
        )
        db.commit()
    except ValueError:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        raise Exception(f"Error al actualizar atributo: {str(e)}")


def delete(db: Session, id_attr: Decimal):
    """
    Elimina atributo si no está referenciado.

    Bloquea borrado cuando hay uso en:
    - categorías (`tab_atributos_categoria`),
    - modelo actual de variantes (`tab_grupos_variante_producto/combinations`),
    - modelo legacy (`tab_product_variant_attributes`).
    """
    try:
        attr_row = db.execute(
            text("SELECT nom_atributo AS name FROM tab_atributos WHERE id_atributo = :id"),
            {"id": id_attr},
        ).first()
        if not attr_row:
            raise ValueError("Atributo no encontrado")

        attr_name = str(attr_row[0] or "").strip()
        ref_ca = db.execute(
            text("SELECT 1 FROM tab_atributos_categoria WHERE id_atributo = :id LIMIT 1"),
            {"id": id_attr}
        ).first()
        if ref_ca:
            raise ValueError("No se puede eliminar: el atributo está asignado a categorías")

        # Modelo actual (variant_groups/combinations)
        if _table_exists(db, "tab_grupos_variante_producto"):
            ref_vg = db.execute(
                text("""
                    SELECT 1
                    FROM tab_grupos_variante_producto
                    WHERE LOWER(TRIM(nom_atributo_dominante)) = LOWER(TRIM(:attr_name))
                    LIMIT 1
                """),
                {"attr_name": attr_name},
            ).first()
            if ref_vg:
                raise ValueError("No se puede eliminar: el atributo está en uso como atributo dominante en variantes")

        if _table_exists(db, "tab_combinaciones_variante_producto"):
            ref_vc = db.execute(
                text("""
                    SELECT 1
                    FROM tab_combinaciones_variante_producto
                    WHERE atributos ? :attr_key
                    LIMIT 1
                """),
                {"attr_key": str(id_attr)},
            ).first()
            if ref_vc:
                raise ValueError("No se puede eliminar: el atributo está en uso en combinaciones de variantes")

        # Modelo legacy (antes de variant_groups)
        if _table_exists(db, "tab_product_variant_attributes"):
            ref_pva = db.execute(
                text("SELECT 1 FROM tab_product_variant_attributes WHERE attribute_id = :id LIMIT 1"),
                {"id": id_attr}
            ).first()
            if ref_pva:
                raise ValueError("No se puede eliminar: el atributo tiene valores en variantes")
        db.execute(text("DELETE FROM tab_atributos WHERE id_atributo = :id"), {"id": id_attr})
        db.commit()
    except ValueError:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        raise Exception(f"Error al eliminar atributo: {str(e)}")


# ---------------------------------------------------------------------------
# Attribute values (tab_valores_atributo)
# ---------------------------------------------------------------------------


def get_values_by_attribute_id(db: Session, attribute_id: Decimal):
    """Lista valores de un atributo, ordenados por `orden` e `id`."""
    try:
        q = text("""
            SELECT id_valor_atributo AS id, id_atributo AS attribute_id,
                   valor AS value, color_hex AS hex_color, orden AS sort_order,
                   ind_activo AS is_active,
                   usr_insert, fec_insert, usr_update, fec_update
            FROM tab_valores_atributo
            WHERE id_atributo = :attribute_id
            ORDER BY orden, id_valor_atributo
        """)
        result = db.execute(q, {"attribute_id": attribute_id})
        return result.mappings().all()
    except Exception as e:
        db.rollback()
        raise Exception(f"Error al obtener valores del atributo: {str(e)}")


def _ensure_attribute_has_predefined_values(db: Session, attribute_id: Decimal) -> None:
    """Garantiza que el atributo admita valores predefinidos antes de crear valores."""
    row = db.execute(
        text("SELECT ind_valores_predefinidos AS has_predefined_values FROM tab_atributos WHERE id_atributo = :id"),
        {"id": attribute_id}
    ).first()
    if not row:
        raise ValueError("Atributo no encontrado")
    if not row[0]:
        raise ValueError("El atributo no usa valores predefinidos; active has_predefined_values primero")


def create_value(
    db: Session,
    attribute_id: Decimal,
    payload: AttributeValueCreate,
    usr_insert: Decimal,
) -> Decimal:
    """
    Crea un valor para un atributo.

    Validaciones:
    - atributo existente y con `has_predefined_values=True`,
    - valor único por atributo (case-insensitive).
    """
    try:
        _ensure_attribute_has_predefined_values(db, attribute_id)
        existing = db.execute(
            text("""
                SELECT 1 FROM tab_valores_atributo
                WHERE id_atributo = :aid AND LOWER(TRIM(valor)) = LOWER(TRIM(:val))
            """),
            {"aid": attribute_id, "val": payload.value}
        ).first()
        if existing:
            raise ValueError("Ya existe un valor con ese nombre en este atributo")
        next_id = db.execute(text("SELECT COALESCE(MAX(id_valor_atributo), 0) + 1 FROM tab_valores_atributo")).scalar()
        db.execute(
            text("""
                INSERT INTO tab_valores_atributo
                    (id_valor_atributo, id_atributo, valor, color_hex, orden, ind_activo, usr_insert)
                VALUES (:id, :attribute_id, :value, :hex_color, :sort_order, :is_active, :usr_insert)
            """),
            {
                "id": next_id,
                "attribute_id": attribute_id,
                "value": payload.value.strip(),
                "hex_color": payload.hex_color.strip() if payload.hex_color else None,
                "sort_order": payload.sort_order,
                "is_active": payload.is_active,
                "usr_insert": usr_insert,
            }
        )
        db.commit()
        return next_id
    except ValueError:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        raise Exception(f"Error al crear valor: {str(e)}")


def update_value(
    db: Session,
    attribute_id: Decimal,
    value_id: Decimal,
    payload: AttributeValueUpdate,
    usr_update: Decimal,
) -> None:
    """
    Actualiza un valor de atributo.

    Validaciones:
    - el valor pertenece al atributo indicado,
    - si cambia texto, mantiene unicidad por atributo.
    """
    try:
        row = db.execute(
            text("SELECT id_valor_atributo FROM tab_valores_atributo WHERE id_valor_atributo = :vid AND id_atributo = :aid"),
            {"vid": value_id, "aid": attribute_id}
        ).first()
        if not row:
            raise ValueError("Valor no encontrado o no pertenece al atributo")
        updates = payload.model_dump(exclude_unset=True)
        if not updates:
            return
        if "value" in updates:
            existing = db.execute(
                text("""
                    SELECT 1 FROM tab_valores_atributo
                    WHERE id_atributo = :aid AND LOWER(TRIM(valor)) = LOWER(TRIM(:val)) AND id_valor_atributo != :vid
                """),
                {"aid": attribute_id, "val": updates["value"], "vid": value_id}
            ).first()
            if existing:
                raise ValueError("Ya existe un valor con ese nombre en este atributo")
            updates["value"] = updates["value"].strip()
        if "hex_color" in updates and updates["hex_color"] is not None:
            updates["hex_color"] = updates["hex_color"].strip() or None
        # Traducir campos Pydantic → columnas DB
        db_updates = {_VAL_COL_MAP.get(k, k): v for k, v in updates.items()}
        set_clause = ", ".join(f"{col} = :{col}" for col in db_updates)
        db_updates["id_valor_atributo"] = value_id
        db_updates["id_atributo"] = attribute_id
        db_updates["usr_update"] = usr_update
        db.execute(
            text(f"UPDATE tab_valores_atributo SET {set_clause}, usr_update = :usr_update WHERE id_valor_atributo = :id_valor_atributo AND id_atributo = :id_atributo"),
            db_updates
        )
        db.commit()
    except ValueError:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        raise Exception(f"Error al actualizar valor: {str(e)}")


def delete_value(db: Session, attribute_id: Decimal, value_id: Decimal) -> None:
    """
    Elimina un valor de atributo cuando no está en uso.

    Bloquea borrado si está referenciado por:
    - `tab_grupos_variante_producto` (valor dominante),
    - `tab_combinaciones_variante_producto` (JSON attributes),
    - `tab_product_variant_attributes` legacy.
    """
    try:
        row = db.execute(
            text("""
                SELECT av.id_valor_atributo AS id, av.valor AS value, a.nom_atributo AS name
                FROM tab_valores_atributo av
                JOIN tab_atributos a ON a.id_atributo = av.id_atributo
                WHERE av.id_valor_atributo = :vid AND av.id_atributo = :aid
            """),
            {"vid": value_id, "aid": attribute_id}
        ).first()
        if not row:
            raise ValueError("Valor no encontrado o no pertenece al atributo")

        value_text = str(row[1] or "").strip()
        attribute_name = str(row[2] or "").strip()

        # Modelo actual (variant_groups/combinations)
        if _table_exists(db, "tab_grupos_variante_producto"):
            ref_vg = db.execute(
                text("""
                    SELECT 1
                    FROM tab_grupos_variante_producto
                    WHERE LOWER(TRIM(nom_atributo_dominante)) = LOWER(TRIM(:attr_name))
                      AND LOWER(TRIM(valor_atributo_dominante)) = LOWER(TRIM(:value_text))
                    LIMIT 1
                """),
                {"attr_name": attribute_name, "value_text": value_text},
            ).first()
            if ref_vg:
                raise ValueError("No se puede eliminar: el valor está en uso como valor dominante en variantes")

        if _table_exists(db, "tab_combinaciones_variante_producto"):
            ref_vc = db.execute(
                text("""
                    SELECT 1
                    FROM tab_combinaciones_variante_producto
                    WHERE LOWER(TRIM(COALESCE(atributos->>:attr_key, ''))) = LOWER(TRIM(:value_text))
                    LIMIT 1
                """),
                {"attr_key": str(attribute_id), "value_text": value_text},
            ).first()
            if ref_vc:
                raise ValueError("No se puede eliminar: el valor está en uso en combinaciones de variantes")

        # Modelo legacy (antes de variant_groups)
        if _table_exists(db, "tab_product_variant_attributes"):
            ref = db.execute(
                text("SELECT 1 FROM tab_product_variant_attributes WHERE attribute_value_id = :vid LIMIT 1"),
                {"vid": value_id}
            ).first()
            if ref:
                raise ValueError("No se puede eliminar: el valor está en uso en variantes de producto")
        db.execute(
            text("DELETE FROM tab_valores_atributo WHERE id_valor_atributo = :vid AND id_atributo = :aid"),
            {"vid": value_id, "aid": attribute_id}
        )
        db.commit()
    except ValueError:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        raise Exception(f"Error al eliminar valor: {str(e)}")
