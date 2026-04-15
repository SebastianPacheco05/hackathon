CREATE OR REPLACE FUNCTION fun_crear_orden_desde_carrito(
    p_id_carrito tab_carritos.id_carrito%TYPE,
    p_id_direccion tab_direcciones_usuario.id_direccion%TYPE,
    p_codigo_descuento tab_descuentos.codigo_descuento%TYPE,
    p_observaciones tab_ordenes.des_observaciones%TYPE,
    p_usr_operacion tab_ordenes.usr_insert%TYPE,
    p_id_canje tab_canjes_puntos_descuentos.id_canje%TYPE DEFAULT NULL,
    p_ind_estado tab_ordenes.ind_estado%TYPE DEFAULT NULL,
    p_metodo_pago tab_ordenes.metodo_pago%TYPE DEFAULT NULL
) RETURNS JSON AS $$
DECLARE
    v_id_usuario tab_usuarios.id_usuario%TYPE;
    v_total_productos DECIMAL(10,2) := 0;
    v_total_descuentos DECIMAL(10,2) := 0;
    v_total_final DECIMAL(10,2) := 0;
    v_id_orden tab_ordenes.id_orden%TYPE;
    v_count_productos INT := 0;
    v_item RECORD;
BEGIN
    SELECT c.id_usuario INTO v_id_usuario
    FROM tab_carritos c
    WHERE c.id_carrito = p_id_carrito;

    IF v_id_usuario IS NULL THEN
        RETURN json_build_object('success', false, 'message', 'El carrito no existe o no pertenece a un usuario registrado');
    END IF;

    SELECT COUNT(1), COALESCE(SUM(cp.cantidad * cp.precio_unitario_carrito), 0)
    INTO v_count_productos, v_total_productos
    FROM tab_carrito_productos cp
    WHERE cp.id_carrito = p_id_carrito;
    IF v_count_productos = 0 THEN
        RETURN json_build_object('success', false, 'message', 'El carrito está vacío');
    END IF;

    IF NOT EXISTS (
        SELECT 1
        FROM tab_direcciones_usuario
        WHERE id_direccion = p_id_direccion
          AND id_usuario = v_id_usuario
          AND ind_activa = TRUE
    ) THEN
        RETURN json_build_object('success', false, 'message', 'La dirección no pertenece al usuario o está inactiva');
    END IF;

    FOR v_item IN
        SELECT
            cp.id_combinacion_variante,
            cp.cantidad,
            cp.precio_unitario_carrito,
            cp.opciones_elegidas,
            cvp.cant_stock
        FROM tab_carrito_productos cp
        JOIN tab_combinaciones_variante_producto cvp
          ON cvp.id_combinacion_variante = cp.id_combinacion_variante
        WHERE cp.id_carrito = p_id_carrito
          AND cvp.ind_activo = TRUE
    LOOP
        IF v_item.cantidad > v_item.cant_stock THEN
            RETURN json_build_object(
                'success', false,
                'message', 'Stock insuficiente en una variante del carrito',
                'id_combinacion_variante', v_item.id_combinacion_variante
            );
        END IF;
    END LOOP;

    SELECT COALESCE(MAX(id_orden), 0) + 1 INTO v_id_orden FROM tab_ordenes;

    v_total_final := v_total_productos - v_total_descuentos;

    INSERT INTO tab_ordenes (
        id_orden, id_usuario, val_total_productos, val_total_descuentos, val_total_pedido,
        ind_estado, metodo_pago, des_observaciones, detalle_descuentos_aplicados, usr_insert, fec_insert
    ) VALUES (
        v_id_orden, v_id_usuario, v_total_productos, v_total_descuentos, v_total_final,
        COALESCE(p_ind_estado, 1), p_metodo_pago, p_observaciones, '[]'::JSON, p_usr_operacion, NOW()
    );

    FOR v_item IN
        SELECT id_combinacion_variante, cantidad, precio_unitario_carrito, COALESCE(opciones_elegidas, '{}'::JSONB) AS opciones_elegidas
        FROM tab_carrito_productos
        WHERE id_carrito = p_id_carrito
    LOOP
        INSERT INTO tab_orden_productos (
            id_orden_producto, id_orden, id_combinacion_variante, cant_producto, precio_unitario_orden, subtotal,
            opciones_elegidas, usr_insert, fec_insert
        ) VALUES (
            (SELECT COALESCE(MAX(id_orden_producto), 0) + 1 FROM tab_orden_productos),
            v_id_orden,
            v_item.id_combinacion_variante,
            v_item.cantidad,
            v_item.precio_unitario_carrito,
            v_item.cantidad * v_item.precio_unitario_carrito,
            v_item.opciones_elegidas,
            p_usr_operacion,
            NOW()
        );
    END LOOP;

    IF COALESCE(p_ind_estado, 1) = 2 THEN
        DELETE FROM tab_carrito_productos WHERE id_carrito = p_id_carrito;
        UPDATE tab_carritos SET usr_update = p_usr_operacion, fec_update = NOW() WHERE id_carrito = p_id_carrito;
    END IF;

    RETURN json_build_object(
        'success', true,
        'message', 'Orden creada exitosamente',
        'id_orden', v_id_orden,
        'id_carrito', p_id_carrito,
        'total_productos', v_total_productos,
        'total_descuentos', v_total_descuentos,
        'total_final', v_total_final,
        'codigo_descuento_aplicado', p_codigo_descuento,
        'id_canje_recibido', p_id_canje,
        'productos_transferidos', v_count_productos
    );
EXCEPTION WHEN OTHERS THEN
    RETURN json_build_object(
        'success', false,
        'message', 'Error al crear la orden: ' || SQLERRM,
        'error_code', SQLSTATE,
        'id_carrito', p_id_carrito
    );
END;
$$ LANGUAGE plpgsql; 