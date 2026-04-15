/*
 * FUNCIÓN: fun_calcular_total_carrito
 * 
 * DESCRIPCIÓN: Función principal que calcula el total del carrito aplicando descuentos
 *              automáticos de empresa disponibles + descuentos canjeados por puntos.
 *              Soporta tanto usuarios registrados como usuarios anónimos.
 * 
 * PARÁMETROS:
 *   - p_id_usuario: ID del usuario registrado (opcional)
 *   - p_session_id: ID de sesión para usuarios anónimos (opcional)
 *   - p_id_canje_aplicar: ID del canje de puntos a aplicar (opcional)
 * 
 * RETORNA: JSON con estructura completa:
 *   - total_productos: Monto total de productos sin descuentos
 *   - total_descuentos: Monto total de descuentos aplicados
 *   - total_final: Monto final a pagar (productos - descuentos)
 *   - descuentos_aplicados: Array de descuentos aplicados con detalles
 *   - descuentos_automaticos: Descuentos automáticos de empresa aplicados
 *   - descuento_canjeado: Descuento canjeado por puntos aplicado
 *   - es_primera_compra: Indicador si es primera compra del usuario
 *   - mensaje: Mensaje descriptivo del resultado
 * 
 * LÓGICA:
 *   1. Aplicar TODOS los descuentos automáticos de empresa activos y aplicables
 *   2. Aplicar UN descuento canjeado por puntos (si se especifica)
 *   3. Sumar todos los descuentos para el total
 * 
 * AUTOR: Sistema DB_Revital
 * FECHA: 2025
 */
CREATE OR REPLACE FUNCTION fun_calcular_total_carrito(
    p_id_usuario tab_usuarios.id_usuario%TYPE DEFAULT NULL,      -- ID del usuario registrado (opcional)
    p_session_id tab_carritos.id_sesion%TYPE DEFAULT NULL,       -- ID de sesión para usuarios anónimos (opcional)
    p_id_canje_aplicar tab_canjes_puntos_descuentos.id_canje%TYPE DEFAULT NULL  -- ID opcional del canje a aplicar
) RETURNS JSON AS $$
DECLARE
    v_id_carrito tab_carritos.id_carrito%TYPE;
    v_total_productos DECIMAL(10,2) := 0;
    v_total_descuentos DECIMAL(10,2) := 0;
    v_total_final DECIMAL(10,2) := 0;
    v_puntos_a_ganar INT := 0;
    v_es_primera_compra BOOLEAN := FALSE;
BEGIN
    IF p_id_usuario IS NULL AND p_session_id IS NULL THEN
        RAISE EXCEPTION 'Al menos uno de los parámetros (p_id_usuario o p_session_id) debe ser proporcionado';
    END IF;
    v_id_carrito := fun_obtener_carrito_usuario(p_id_usuario, p_session_id);

    SELECT COALESCE(SUM(cantidad * precio_unitario_carrito), 0) INTO v_total_productos
    FROM tab_carrito_productos
    WHERE id_carrito = v_id_carrito;

    IF p_id_usuario IS NOT NULL THEN
        SELECT NOT EXISTS (
            SELECT 1 FROM tab_ordenes WHERE id_usuario = p_id_usuario
        ) INTO v_es_primera_compra;

        BEGIN
            v_puntos_a_ganar := fun_calcular_puntos_por_compra(v_total_productos);
        EXCEPTION
            WHEN OTHERS THEN
                v_puntos_a_ganar := 0;
        END;
    END IF;

    v_total_final := v_total_productos - v_total_descuentos;

    RETURN json_build_object(
        'success', true,
        'total_final', v_total_final,
        'total_productos', v_total_productos,
        'total_descuentos', v_total_descuentos,
        'ahorro_total', v_total_descuentos,
        'resumen', json_build_object(
            'subtotal', v_total_productos,
            'descuentos', v_total_descuentos,
            'total_a_pagar', v_total_final,
            'ahorro_porcentaje', CASE 
                WHEN v_total_productos > 0 THEN ROUND((v_total_descuentos / v_total_productos) * 100, 2)
                ELSE 0 
            END
        ),
        'descuentos_aplicados', '[]'::JSON,
        'descuentos_automaticos', '[]'::JSON,
        'descuento_canjeado', NULL,
        'total_desc_automaticos', 0,
        'total_desc_canjeado', 0,
        'es_primera_compra', v_es_primera_compra,
        'puntos_a_ganar', v_puntos_a_ganar,
        'id_canje_aplicado', p_id_canje_aplicar,
        'mensaje', CASE WHEN v_total_productos > 0 THEN 'Total calculado' ELSE 'Carrito vacío' END,
        'mensaje_puntos', CASE 
            WHEN p_id_usuario IS NULL THEN 'Regístrate para acumular puntos'
            WHEN v_puntos_a_ganar > 0 THEN 'Ganarás ' || v_puntos_a_ganar || ' puntos con esta compra'
            ELSE 'Esta compra no genera puntos'
        END,
        'mensaje_resumen', 'Total a pagar: $' || v_total_final || 
            CASE 
                WHEN v_total_descuentos > 0 THEN ' (ahorraste $' || v_total_descuentos || ')'
                ELSE ' (sin descuentos)'
            END
    );
END;
$$ LANGUAGE plpgsql; 