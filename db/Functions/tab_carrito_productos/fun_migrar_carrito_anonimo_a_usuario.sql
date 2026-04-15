/*
 * Migra el carrito anónimo al carrito del usuario registrado.
 * Usa id_combinacion_variante en tab_carrito_productos; actualiza precio desde tab_combinaciones_variante_producto.
 *
 * IMPORTANTE: Solo migra y elimina si el carrito origen es anónimo (id_usuario IS NULL).
 * Si el carrito ya pertenece al usuario (p. ej. checkout en curso), no se elimina para evitar
 * que confirm-checkout falle al no encontrar el carrito de la referencia.
 */
CREATE OR REPLACE FUNCTION fun_migrar_carrito_anonimo_a_usuario(
    p_id_carrito_anonimo tab_carritos.id_carrito%TYPE,
    p_id_usuario tab_usuarios.id_usuario%TYPE,
    p_usr_operacion tab_carritos.usr_insert%TYPE
) RETURNS JSON AS $$
DECLARE
    v_id_carrito_usuario tab_carritos.id_carrito%TYPE;
    v_item RECORD;
    v_precio DECIMAL(12,2);
    v_carrito_es_anonimo BOOLEAN;
BEGIN
    -- Verificar que el carrito origen sea anónimo (id_usuario IS NULL).
    -- Si ya es del usuario, no migrar ni eliminar (evita borrar carrito de checkout en curso).
    SELECT (c.id_usuario IS NULL) INTO v_carrito_es_anonimo
    FROM tab_carritos c
    WHERE c.id_carrito = p_id_carrito_anonimo;

    IF NOT FOUND OR NOT v_carrito_es_anonimo THEN
        RETURN json_build_object('success', true, 'message', 'Carrito ya pertenece al usuario o no existe');
    END IF;

    v_id_carrito_usuario := fun_obtener_carrito_usuario(p_id_usuario, NULL);

    FOR v_item IN
        SELECT id_combinacion_variante, cantidad, precio_unitario_carrito, COALESCE(opciones_elegidas, '{}'::JSONB) AS opciones_elegidas
        FROM tab_carrito_productos
        WHERE id_carrito = p_id_carrito_anonimo
    LOOP
        SELECT precio INTO v_precio
        FROM tab_combinaciones_variante_producto
        WHERE id_combinacion_variante = v_item.id_combinacion_variante AND ind_activo = TRUE;
        v_precio := COALESCE(v_precio, v_item.precio_unitario_carrito);

        INSERT INTO tab_carrito_productos (id_carrito, id_combinacion_variante, cantidad, precio_unitario_carrito, opciones_elegidas, usr_insert)
        VALUES (v_id_carrito_usuario, v_item.id_combinacion_variante, v_item.cantidad, v_precio, v_item.opciones_elegidas, COALESCE(p_usr_operacion, p_id_usuario))
        ON CONFLICT (id_carrito, id_combinacion_variante)
        DO UPDATE SET
            cantidad = tab_carrito_productos.cantidad + v_item.cantidad,
            precio_unitario_carrito = v_precio,
            opciones_elegidas = COALESCE(EXCLUDED.opciones_elegidas, tab_carrito_productos.opciones_elegidas, '{}'::JSONB),
            usr_update = p_usr_operacion,
            fec_update = NOW();
    END LOOP;

    DELETE FROM tab_carrito_productos WHERE id_carrito = p_id_carrito_anonimo;
    DELETE FROM tab_carritos WHERE id_carrito = p_id_carrito_anonimo;

    RETURN json_build_object('success', true, 'message', 'Carrito migrado exitosamente');
END;
$$ LANGUAGE plpgsql;
