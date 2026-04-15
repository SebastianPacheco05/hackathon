/*
 * FUNCIÓN: fun_obtener_pago
 * 
 * DESCRIPCIÓN: Obtiene la información de un pago a partir del ID de la orden.
 * 
 * PARÁMETROS:
 *   - p_id_orden: ID de la orden en nuestro sistema.
 * 
 * RETORNA: JSON - Un objeto con los detalles del pago o un mensaje de error.
 * 
 * LÓGICA:
 *   1. Busca el pago asociado a la orden.
 *   2. Si lo encuentra, devuelve sus detalles en formato JSON.
 *   3. Si no, devuelve un mensaje indicando que no se encontró.
 * 
 * AUTOR: Sistema DB_Revital
 * FECHA: 2025
 */
CREATE OR REPLACE FUNCTION fun_obtener_pago(
    p_id_orden tab_ordenes.id_orden%TYPE
) RETURNS JSON AS $$
DECLARE
    v_pago_info RECORD;
BEGIN
    -- VALIDACIÓN
    IF p_id_orden IS NULL THEN
        RETURN json_build_object('success', false, 'message', 'El ID de la orden es obligatorio.');
    END IF;

    -- CONSULTA (evitar SELECT *; traer columnas explícitas)
    SELECT 
        id_pago,
        id_orden,
        ref_pago,
        id_transaccion_proveedor,
        cod_proveedor_pago,
        estado_pago,
        detalle_estado_pago,
        monto,
        cod_moneda,
        num_cuotas,
        tipo_medio_pago,
        datos_extra_medio_pago,
        monto_comision,
        monto_neto_recibido,
        fec_creacion_proveedor,
        fec_aprobacion_proveedor,
        respuesta_cruda,
        ultimo_evento_crudo,
        id_pago_padre,
        estado_procesamiento,
        usr_insert,
        fec_insert,
        usr_update,
        fec_update
    INTO v_pago_info
    FROM tab_pagos
    WHERE id_orden = p_id_orden
    ORDER BY fec_insert DESC
    LIMIT 1;

    -- RESPUESTA
    IF NOT FOUND THEN
        RETURN json_build_object('success', false, 'message', 'No se encontró información de pago para la orden especificada.');
    END IF;

    RETURN json_build_object(
        'success', true,
        'pago', row_to_json(v_pago_info)
    );

EXCEPTION 
    WHEN OTHERS THEN
        RETURN json_build_object('success', false, 'message', 'Error inesperado: ' || SQLERRM);
END;
$$ LANGUAGE plpgsql; 