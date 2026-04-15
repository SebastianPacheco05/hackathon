/*
 * Actualiza un producto en la tabla products. Si cambia el nombre, se regenera el slug_producto.
 */
CREATE OR REPLACE FUNCTION fun_update_producto(
    p_id DECIMAL,
    p_category_id DECIMAL DEFAULT NULL,
    p_name VARCHAR DEFAULT NULL,
    p_description TEXT DEFAULT NULL,
    p_id_marca DECIMAL DEFAULT NULL,
    p_is_active BOOLEAN DEFAULT NULL,
    p_usr_operacion DECIMAL(10) DEFAULT NULL,
    p_id_proveedor DECIMAL DEFAULT NULL
) RETURNS VARCHAR AS $$
DECLARE
    v_slug VARCHAR;
BEGIN
    IF p_id IS NULL OR NOT EXISTS (SELECT 1 FROM tab_productos WHERE id_producto = p_id) THEN
        RETURN 'Error: Producto no encontrado.';
    END IF;
    IF p_category_id IS NOT NULL AND NOT EXISTS (SELECT 1 FROM tab_categorias WHERE id_categoria = p_category_id) THEN
        RETURN 'Error: id_categoria no existe.';
    END IF;
    IF p_id_marca IS NOT NULL AND NOT EXISTS (SELECT 1 FROM tab_marcas WHERE id_marca = p_id_marca) THEN
        RETURN 'Error: id_marca no existe.';
    END IF;
    IF p_id_proveedor IS NOT NULL AND NOT EXISTS (SELECT 1 FROM tab_proveedores WHERE id_proveedor = p_id_proveedor) THEN
        RETURN 'Error: id_proveedor no existe.';
    END IF;
    IF p_name IS NOT NULL AND length(trim(p_name)) < 2 THEN
        RETURN 'Error: Nombre debe tener al menos 2 caracteres.';
    END IF;

    IF p_name IS NOT NULL THEN
        v_slug := fun_generate_unique_slug(trim(p_name), 'tab_productos', p_id);
    ELSE
        SELECT slug_producto INTO v_slug FROM tab_productos WHERE id_producto = p_id;
    END IF;

    UPDATE tab_productos SET
        id_categoria = COALESCE(p_category_id, id_categoria),
        nom_producto = COALESCE(trim(p_name), nom_producto),
        slug_producto = v_slug,
        descripcion = CASE WHEN p_description IS NOT NULL THEN p_description ELSE descripcion END,
        id_marca = CASE WHEN p_id_marca IS NOT NULL THEN p_id_marca ELSE id_marca END,
        ind_activo = COALESCE(p_is_active, ind_activo),
        usr_update = p_usr_operacion,
        fec_update = CURRENT_TIMESTAMP,
        id_proveedor = p_id_proveedor
    WHERE id_producto = p_id;

    IF FOUND THEN RETURN 'Producto actualizado correctamente'; ELSE RETURN 'Error al actualizar'; END IF;
EXCEPTION
    WHEN unique_violation THEN RETURN 'Error: Slug duplicado.';
    WHEN OTHERS THEN RETURN 'Error: ' || SQLERRM;
END;
$$ LANGUAGE plpgsql;
