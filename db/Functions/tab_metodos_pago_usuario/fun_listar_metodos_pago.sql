/*
 * FUNCIÓN: fun_listar_metodos_pago
 * 
 * DESCRIPCIÓN: Lista todos los métodos de pago guardados por un usuario.
 * 
 * PARÁMETROS:
 *   - p_id_usuario: ID del usuario (obligatorio)
 * 
 * RETORNA: TABLE - Una tabla con los detalles de los métodos de pago.
 * 
 * LÓGICA:
 *   1. Busca todos los métodos de pago asociados al ID del usuario.
 *   2. Ordena los resultados para mostrar el método por defecto primero.
 * 
 * AUTOR: Sistema DB_Revital
 * FECHA: 2025
 */
CREATE OR REPLACE FUNCTION fun_listar_metodos_pago(
    p_id_usuario tab_usuarios.id_usuario%TYPE
) RETURNS TABLE (
    id_metodo_pago INT,
    cod_proveedor_pago VARCHAR(50),
    marca_tarjeta VARCHAR(50),
    ultimos_cuatro_digitos VARCHAR(4),
    mes_vencimiento INT,
    ano_vencimiento INT,
    ind_predeterminado BOOLEAN
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        mpu.id_metodo_pago,
        mpu.cod_proveedor_pago,
        mpu.marca_tarjeta,
        mpu.ultimos_cuatro_digitos,
        mpu.mes_vencimiento,
        mpu.ano_vencimiento,
        mpu.ind_predeterminado
    FROM
        tab_metodos_pago_usuario mpu
    WHERE
        mpu.id_usuario = p_id_usuario
    ORDER BY
        mpu.ind_predeterminado DESC, mpu.fec_insert DESC;
END;
$$ LANGUAGE plpgsql; 