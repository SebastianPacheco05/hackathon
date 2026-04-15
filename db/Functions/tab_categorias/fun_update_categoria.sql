/*
 * Actualiza una categoría en la tabla tab_categorias.
 * Si cambia el nombre, se regenera el slug_producto.
 */
CREATE OR REPLACE FUNCTION fun_update_categoria(
    p_id DECIMAL,
    p_name VARCHAR,
    p_parent_id DECIMAL DEFAULT NULL,
    p_is_active BOOLEAN DEFAULT NULL,
    p_usr_operacion DECIMAL(10) DEFAULT NULL
) RETURNS VARCHAR AS $$
DECLARE
    v_slug VARCHAR;
BEGIN
    IF p_id IS NULL OR NOT EXISTS (SELECT 1 FROM tab_categorias WHERE id = p_id) THEN
        RETURN 'Error: Categoría no encontrada.';
    END IF;
    IF p_name IS NULL OR trim(p_name) = '' OR length(trim(p_name)) < 2 THEN
        RETURN 'Error: El nombre es obligatorio y debe tener al menos 2 caracteres.';
    END IF;
    IF p_parent_id IS NOT NULL AND NOT EXISTS (SELECT 1 FROM tab_categorias WHERE id = p_parent_id) THEN
        RETURN 'Error: La categoría padre no existe.';
    END IF;
    IF p_parent_id IS NOT NULL AND p_parent_id = p_id THEN
        RETURN 'Error: Una categoría no puede ser padre de sí misma.';
    END IF;

    v_slug := fun_generate_unique_slug(p_name, 'tab_categorias', p_id);

    UPDATE tab_categorias SET
        nom_producto = trim(p_name),
        slug_producto = v_slug,
        id_categoria_padre = p_parent_id,
        ind_activo = COALESCE(p_is_active, ind_activo),
        usr_update = p_usr_operacion,
        fec_update = CURRENT_TIMESTAMP
    WHERE id = p_id;

    IF FOUND THEN
        RETURN 'Categoría actualizada correctamente';
    ELSE
        RETURN 'Error al actualizar la categoría';
    END IF;
EXCEPTION
    WHEN unique_violation THEN
        RETURN 'Error: Slug duplicado.';
    WHEN OTHERS THEN
        RETURN 'Error: ' || SQLERRM;
END;
$$ LANGUAGE plpgsql;
