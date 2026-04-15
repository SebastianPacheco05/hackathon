/*
 * Restaura cant_stock de variantes cuando una orden pasa a estado cancelado (ind_estado = 4).
 * Usa tab_orden_productos.id_combinacion_variante (combination id) y tab_combinaciones_variante_producto.
 */
CREATE OR REPLACE FUNCTION fun_restaurar_stock_cancelacion()
RETURNS TRIGGER AS $$
DECLARE
    v_record RECORD;
    v_stock_actual INT;
    v_stock_nuevo INT;
    v_count INT := 0;
BEGIN
    IF OLD.ind_estado = 4 OR NEW.ind_estado != 4 THEN
        RETURN NULL;
    END IF;

    FOR v_record IN
        SELECT op.id_orden_producto, op.id_combinacion_variante, op.cant_producto, p.nom_producto AS nom_producto
        FROM tab_orden_productos op
        JOIN tab_combinaciones_variante_producto pv ON pv.id_combinacion_variante = op.id_combinacion_variante
        JOIN tab_grupos_variante_producto g ON g.id_grupo_variante = pv.id_grupo_variante
        JOIN tab_productos p ON p.id_producto = g.id_producto
        WHERE op.id_orden = NEW.id_orden
    LOOP
        SELECT cant_stock INTO v_stock_actual
        FROM tab_combinaciones_variante_producto
        WHERE id_combinacion_variante = v_record.id_combinacion_variante;

        v_stock_nuevo := v_stock_actual + v_record.cant_producto;

        UPDATE tab_combinaciones_variante_producto
        SET cant_stock = v_stock_nuevo, usr_update = COALESCE(NEW.usr_update, 1000000000), fec_update = NOW()
        WHERE id_combinacion_variante = v_record.id_combinacion_variante;

        INSERT INTO tab_movimientos_inventario (
            id_combinacion_variante, tipo_movimiento, cantidad,
            stock_anterior, stock_actual,
            id_orden_usuario_detalle, descripcion, usr_insert
        ) VALUES (
            v_record.id_combinacion_variante,
            'devolucion_usuario',
            v_record.cant_producto,
            v_stock_actual,
            v_stock_nuevo,
            v_record.id_orden_producto,
            'Devolución por cancelación - Orden #' || NEW.id_orden || ' - ' || v_record.nom_producto,
            COALESCE(NEW.usr_update, 1000000000)
        );

        v_count := v_count + 1;
    END LOOP;

    RETURN NULL;
EXCEPTION
    WHEN OTHERS THEN
        RAISE EXCEPTION 'Error en restauración de cant_stock para orden #%: %', NEW.id_orden, SQLERRM;
END;
$$ LANGUAGE plpgsql;
