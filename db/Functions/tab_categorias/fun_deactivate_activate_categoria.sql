/*
 * Activa o desactiva una categoría y en cascada todas sus subcategorías (árbol)
 * y todos los productos en esas categorías. Usa tabla tab_categorias.
 */
CREATE OR REPLACE FUNCTION fun_deactivate_activate_categoria(
    p_id_categoria DECIMAL,
    p_activar BOOLEAN,
    p_usr_operacion DECIMAL(10) DEFAULT NULL
) RETURNS VARCHAR AS $$
DECLARE
    v_estado_actual BOOLEAN;
    v_count_categorias INT := 0;
    v_count_productos INT := 0;
    v_accion TEXT;
BEGIN
    SELECT ind_activo INTO v_estado_actual FROM tab_categorias WHERE id_categoria = p_id_categoria;
    IF v_estado_actual IS NULL THEN
        RETURN 'Error: Categoría no encontrada';
    END IF;
    IF v_estado_actual = p_activar THEN
        RETURN FORMAT('Error: La categoría ya está %s', CASE WHEN p_activar THEN 'activa' ELSE 'inactiva' END);
    END IF;

    v_accion := CASE WHEN p_activar THEN 'activada' ELSE 'desactivada' END;

    WITH RECURSIVE tree AS (
        SELECT id_categoria FROM tab_categorias WHERE id_categoria = p_id_categoria
        UNION ALL
        SELECT c.id_categoria FROM tab_categorias c
        INNER JOIN tree t ON c.id_categoria_padre = t.id_categoria
    )
    UPDATE tab_categorias SET ind_activo = p_activar, usr_update = p_usr_operacion, fec_update = CURRENT_TIMESTAMP
    WHERE id_categoria IN (SELECT id_categoria FROM tree);
    GET DIAGNOSTICS v_count_categorias = ROW_COUNT;

    WITH RECURSIVE tree AS (
        SELECT id_categoria FROM tab_categorias WHERE id_categoria = p_id_categoria
        UNION ALL
        SELECT c.id_categoria FROM tab_categorias c INNER JOIN tree t ON c.id_categoria_padre = t.id_categoria
    )
    UPDATE tab_productos SET ind_activo = p_activar, usr_update = p_usr_operacion, fec_update = CURRENT_TIMESTAMP
    WHERE id_categoria IN (SELECT id_categoria FROM tree);
    GET DIAGNOSTICS v_count_productos = ROW_COUNT;

    RETURN FORMAT('Categoría %s exitosamente. Se actualizaron %s categoría(s) y %s producto(s).',
        v_accion, v_count_categorias, v_count_productos);
EXCEPTION
    WHEN OTHERS THEN
        RETURN 'Error: ' || SQLERRM;
END;
$$ LANGUAGE plpgsql;
