/*
 * Elimina un producto: borra imágenes, atributos de variantes, variantes y producto.
 * No permite eliminar si hay ítems en carrito o en órdenes con sus variantes.
 */
CREATE OR REPLACE FUNCTION fun_delete_producto(p_id DECIMAL)
RETURNS JSON AS $$
DECLARE
    v_carrito INT;
    v_orden INT;
BEGIN
    IF p_id IS NULL OR NOT EXISTS (SELECT 1 FROM tab_productos WHERE id_producto = p_id) THEN
        RETURN json_build_object('success', false, 'message', 'Producto no encontrado', 'id_producto', p_id);
    END IF;
    SELECT COUNT(1) INTO v_carrito
    FROM tab_carrito_productos cp
    JOIN tab_combinaciones_variante_producto pv ON cp.id_combinacion_variante = pv.id_combinacion_variante
    JOIN tab_grupos_variante_producto g ON g.id_grupo_variante = pv.id_grupo_variante
    WHERE g.id_producto = p_id;
    IF v_carrito > 0 THEN
        RETURN json_build_object('success', false, 'message', 'No se puede eliminar: hay ítems en carrito', 'id_producto', p_id);
    END IF;
    SELECT COUNT(1) INTO v_orden
    FROM tab_orden_productos op
    JOIN tab_combinaciones_variante_producto pv ON op.id_combinacion_variante = pv.id_combinacion_variante
    JOIN tab_grupos_variante_producto g ON g.id_grupo_variante = pv.id_grupo_variante
    WHERE g.id_producto = p_id;
    IF v_orden > 0 THEN
        RETURN json_build_object('success', false, 'message', 'No se puede eliminar: hay ítems en órdenes', 'id_producto', p_id);
    END IF;

    DELETE FROM tab_imagenes_grupo_variante WHERE id_grupo_variante IN (SELECT id_grupo_variante FROM tab_grupos_variante_producto WHERE id_producto = p_id);
    DELETE FROM tab_combinaciones_variante_producto WHERE id_grupo_variante IN (SELECT id_grupo_variante FROM tab_grupos_variante_producto WHERE id_producto = p_id);
    DELETE FROM tab_grupos_variante_producto WHERE id_producto = p_id;
    DELETE FROM tab_estadisticas_productos WHERE id_producto = p_id;
    DELETE FROM tab_favoritos WHERE id_producto = p_id;
    DELETE FROM tab_comentarios WHERE id_producto = p_id;
    DELETE FROM tab_productos WHERE id_producto = p_id;

    RETURN json_build_object('success', true, 'message', 'Producto eliminado', 'id_producto', p_id);
EXCEPTION
    WHEN OTHERS THEN
        RETURN json_build_object('success', false, 'message', 'Error: ' || SQLERRM, 'id_producto', p_id);
END;
$$ LANGUAGE plpgsql;
