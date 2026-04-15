/*
 * FUNCIÓN: fun_agregar_metodo_pago
 * 
 * DESCRIPCIÓN: Agrega un nuevo método de pago (tarjeta tokenizada) a un usuario.
 *              Se utiliza para guardar tarjetas para futuras compras.
 * 
 * PARÁMETROS:
 *   - p_id_usuario: ID del usuario (obligatorio)
 *   - p_provider_name: Nombre del proveedor de pago (ej. 'mercadopago')
 *   - p_provider_card_id: ID de la tarjeta en el proveedor (token)
 *   - p_brand: Marca de la tarjeta (ej. 'Visa')
 *   - p_last_four_digits: Últimos 4 dígitos de la tarjeta
 *   - p_expiration_month: Mes de expiración
 *   - p_expiration_year: Año de expiración
 *   - p_usr_operacion: Usuario que realiza la operación (para auditoría)
 * 
 * RETORNA: JSON - Resultado de la operación
 * 
 * LÓGICA:
 *   1. Validar parámetros de entrada.
 *   2. Verificar que la tarjeta no exista ya para ese usuario y proveedor.
 *   3. Insertar el nuevo método de pago.
 * 
 * AUTOR: Sistema DB_Revital
 * FECHA: 2025
 */
CREATE OR REPLACE FUNCTION fun_agregar_metodo_pago(
    p_id_usuario tab_usuarios.id_usuario%TYPE,
    p_provider_name tab_metodos_pago_usuario.cod_proveedor_pago%TYPE,
    -- CAMBIO: Renombrado para alinearse con Wompi
    p_provider_source_id tab_metodos_pago_usuario.id_fuente_proveedor%TYPE,
    p_brand tab_metodos_pago_usuario.marca_tarjeta%TYPE,
    p_last_four_digits tab_metodos_pago_usuario.ultimos_cuatro_digitos%TYPE,
    p_expiration_month tab_metodos_pago_usuario.mes_vencimiento%TYPE,
    p_expiration_year tab_metodos_pago_usuario.ano_vencimiento%TYPE,
    -- AÑADIDO: Para guardar el titular de la tarjeta
    p_card_holder tab_metodos_pago_usuario.titular_tarjeta%TYPE,
    p_usr_operacion tab_usuarios.id_usuario%TYPE
) RETURNS JSON AS $$
DECLARE
    v_id_metodo_pago INT;
    v_new_payment_method JSON;
BEGIN
    -- VALIDACIONES
    IF p_id_usuario IS NULL OR p_provider_source_id IS NULL OR p_last_four_digits IS NULL THEN
        RETURN json_build_object('success', false, 'message', 'ID de usuario, ID de fuente de pago y últimos 4 dígitos son obligatorios');
    END IF;

    -- INSERCIÓN
    INSERT INTO tab_metodos_pago_usuario (
        id_usuario,
        cod_proveedor_pago,
        id_fuente_proveedor,
        marca_tarjeta,
        ultimos_cuatro_digitos,
        mes_vencimiento,
        ano_vencimiento,
        titular_tarjeta,
        usr_insert
    ) VALUES (
        p_id_usuario,
        p_provider_name,
        p_provider_source_id,
        p_brand,
        p_last_four_digits,
        p_expiration_month,
        p_expiration_year,
        p_card_holder,
        p_usr_operacion
    )
    ON CONFLICT (id_usuario, id_fuente_proveedor, cod_proveedor_pago) DO NOTHING
    RETURNING id_metodo_pago INTO v_id_metodo_pago;

    -- RESPUESTA
    IF v_id_metodo_pago IS NULL THEN
        RETURN json_build_object(
            'success', false,
            'message', 'El método de pago ya existe para este usuario.'
        );
    END IF;

    -- Devolver el registro completo para usar en la API
    SELECT json_build_object(
        'id_metodo_pago', m.id_metodo_pago,
        'id_fuente_proveedor', m.id_fuente_proveedor,
        'brand', m.marca_tarjeta,
        'last_four_digits', m.ultimos_cuatro_digitos,
        'card_holder', m.titular_tarjeta,
        'is_default', m.ind_predeterminado
    ) INTO v_new_payment_method
    FROM tab_metodos_pago_usuario m WHERE m.id_metodo_pago = v_id_metodo_pago;

    RETURN json_build_object(
        'success', true,
        'message', 'Método de pago agregado exitosamente.',
        'data', v_new_payment_method
    );

EXCEPTION
    WHEN OTHERS THEN
        RETURN json_build_object(
            'success', false,
            'message', 'Error inesperado: ' || SQLERRM
        );
END;
$$ LANGUAGE plpgsql;