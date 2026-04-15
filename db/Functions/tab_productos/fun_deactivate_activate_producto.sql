/*
 * Activa o desactiva un producto y todas sus variantes (product_variants).
 */
CREATE OR REPLACE FUNCTION fun_deactivate_activate_producto(
    p_id_producto DECIMAL,
    p_activar BOOLEAN,
    p_usr_operacion DECIMAL(10) DEFAULT NULL
) RETURNS VARCHAR AS $$
DECLARE
    v_estado BOOLEAN;
    v_var INT;
BEGIN
    SELECT ind_activo INTO v_estado FROM tab_productos WHERE id_producto = p_id_producto;
    IF v_estado IS NULL THEN
        RETURN 'Error: Producto no encontrado';
    END IF;
    IF v_estado = p_activar THEN
        RETURN FORMAT('Error: El producto ya está %s', CASE WHEN p_activar THEN 'activo' ELSE 'inactivo' END);
    END IF;
    UPDATE tab_productos SET ind_activo = p_activar, usr_update = p_usr_operacion, fec_update = CURRENT_TIMESTAMP WHERE id_producto = p_id_producto;
    UPDATE tab_grupos_variante_producto SET ind_activo = p_activar, usr_update = p_usr_operacion, fec_update = CURRENT_TIMESTAMP WHERE id_producto = p_id_producto;
    UPDATE tab_combinaciones_variante_producto c SET ind_activo = p_activar, usr_update = p_usr_operacion, fec_update = CURRENT_TIMESTAMP
    WHERE c.id_grupo_variante IN (SELECT id_grupo_variante FROM tab_grupos_variante_producto WHERE id_producto = p_id_producto);
    GET DIAGNOSTICS v_var = ROW_COUNT;
    RETURN FORMAT('Producto %s. Combinaciones actualizadas: %s.', CASE WHEN p_activar THEN 'activado' ELSE 'desactivado' END, v_var);
EXCEPTION
    WHEN OTHERS THEN RETURN 'Error: ' || SQLERRM;
END;
$$ LANGUAGE plpgsql;
