/*
 * Elimina un producto de favoritos del usuario. Usa id_producto.
 */
CREATE OR REPLACE FUNCTION fun_delete_favorito(
    p_id_usuario tab_usuarios.id_usuario%TYPE,
    p_product_id tab_productos.id_producto%TYPE
) RETURNS VARCHAR AS $$
BEGIN
    IF p_id_usuario IS NULL OR p_product_id IS NULL THEN
        RETURN 'Error: id_usuario y id_producto son obligatorios.';
    END IF;
    DELETE FROM tab_favoritos
    WHERE id_usuario = p_id_usuario AND id_producto = p_product_id;
    IF FOUND THEN
        RETURN 'Favorito eliminado correctamente';
    ELSE
        RETURN 'Error: El favorito no existe o ya fue eliminado';
    END IF;
END;
$$ LANGUAGE plpgsql;
