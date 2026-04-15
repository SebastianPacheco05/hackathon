/*
 * FUNCIÓN: fun_obtener_carrito_usuario
 * 
 * DESCRIPCIÓN: Obtiene el carrito existente de un usuario o crea uno nuevo si no existe.
 *              Maneja tanto usuarios registrados como usuarios anónimos mediante id_sesion.
 * 
 * PARÁMETROS:
 *   - p_id_usuario: ID del usuario registrado (opcional)
 *   - p_session_id: ID de sesión para usuarios anónimos (opcional)
 * 
 * RETORNA: INTEGER - ID del carrito
 * 
 * LÓGICA:
 *   1. Si p_id_usuario no es NULL: busca carrito por ID de usuario
 *   2. Si p_session_id no es NULL: busca carrito anónimo por id_sesion
 *   3. Si no encuentra carrito existente: crea uno nuevo
 * 
 * NOTA: Al menos uno de los parámetros debe ser proporcionado
 * 
 * AUTOR: Sistema DB_Revital
 * FECHA: 2024
 */
CREATE OR REPLACE FUNCTION fun_obtener_carrito_usuario(
    p_id_usuario tab_usuarios.id_usuario%TYPE,
    p_session_id tab_carritos.id_sesion%TYPE
) RETURNS tab_carritos.id_carrito%TYPE AS $$
DECLARE
    -- Variable para almacenar el ID del carrito encontrado o creado
    v_id_carrito tab_carritos.id_carrito%TYPE;
    v_next_id tab_carritos.id_carrito%TYPE;
    v_usr_insert DECIMAL(10);
BEGIN
    -- Validar que al menos un parámetro no sea NULL
    IF p_id_usuario IS NULL AND p_session_id IS NULL THEN
        RAISE EXCEPTION 'Al menos uno de los parámetros (p_id_usuario o p_session_id) debe ser proporcionado';
    END IF;
    
    -- Determinar el usuario para auditoría
    IF p_id_usuario IS NOT NULL THEN
        v_usr_insert := p_id_usuario;
    ELSE
        -- Para usuarios anónimos, usar un ID temporal basado en el hash del id_sesion
        v_usr_insert := ABS(hashtext(p_session_id))::DECIMAL(10);
    END IF;
    
    -- Buscar carrito existente según el tipo de usuario
    IF p_id_usuario IS NOT NULL THEN
        -- CASO 1: Usuario registrado - buscar por ID de usuario
        SELECT id_carrito INTO v_id_carrito 
        FROM tab_carritos 
        WHERE id_usuario = p_id_usuario
        ORDER BY fec_update DESC    -- Obtener el más reciente
        LIMIT 1;
        
    ELSIF p_session_id IS NOT NULL THEN 
        -- CASO 2: Usuario anónimo - buscar por id_sesion
        SELECT id_carrito INTO v_id_carrito
        FROM tab_carritos
        WHERE id_sesion = p_session_id
        AND id_usuario IS NULL                   -- Asegurar que es carrito anónimo
        ORDER BY fec_update DESC    -- Obtener el más reciente
        LIMIT 1;
    END IF;
    
    -- Si no existe carrito, crear uno nuevo
    IF v_id_carrito IS NULL THEN
        SELECT COALESCE(MAX(id_carrito), 0) + 1
        INTO v_next_id
        FROM tab_carritos;

        INSERT INTO tab_carritos (id_carrito, id_usuario, id_sesion, usr_insert)
        VALUES (
            v_next_id,
            p_id_usuario, 
            p_session_id,
            v_usr_insert  -- Usuario para auditoría (sin COALESCE)
        )
        RETURNING id_carrito INTO v_id_carrito;
    END IF;
    
    -- Retornar ID del carrito (existente o recién creado)
    RETURN v_id_carrito;
END;
$$ LANGUAGE plpgsql; 