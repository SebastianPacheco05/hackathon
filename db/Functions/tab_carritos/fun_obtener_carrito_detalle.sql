/*
 * Obtiene el detalle del carrito con id_combinacion_variante (combination id); join a variant_combinations/groups y products.
 */
CREATE OR REPLACE FUNCTION fun_obtener_carrito_detalle(
    p_id_usuario tab_usuarios.id_usuario%TYPE,
    p_session_id tab_carritos.id_sesion%TYPE
) RETURNS JSON AS $$
DECLARE
    v_id_carrito tab_carritos.id_carrito%TYPE;
    v_resultado JSON;
BEGIN
    v_id_carrito := fun_obtener_carrito_usuario(p_id_usuario, p_session_id);

    SELECT json_build_object(
        'id_carrito', v_id_carrito,
        'total_productos', COALESCE(COUNT(cp.id_carrito_producto), 0),
        'subtotal_carrito', COALESCE(SUM(cp.cantidad * cp.precio_unitario_carrito), 0),
        'productos', COALESCE(
            json_agg(
                json_build_object(
                    'id_carrito_producto', cp.id_carrito_producto,
                    'id_combinacion_variante', cp.id_combinacion_variante,
                    'id_producto', p.id_producto,
                    'nombre_producto', p.nom_producto,
                    'cantidad', cp.cantidad,
                    'precio_unitario', cp.precio_unitario_carrito,
                    'subtotal', (cp.cantidad * cp.precio_unitario_carrito),
                    'stock_disponible', pv.cant_stock,
                    'opciones_elegidas', COALESCE(cp.opciones_elegidas, '{}'::JSONB),
                    'imagen_producto', (SELECT igv.url_imagen FROM tab_imagenes_grupo_variante igv WHERE igv.id_grupo_variante = g.id_grupo_variante ORDER BY igv.orden, igv.id_imagen_grupo_variante LIMIT 1)
                ) ORDER BY cp.fec_insert DESC
            ),
            '[]'::json
        )
    ) INTO v_resultado
    FROM tab_carrito_productos cp
    JOIN tab_combinaciones_variante_producto pv ON pv.id_combinacion_variante = cp.id_combinacion_variante AND pv.ind_activo = TRUE
    JOIN tab_grupos_variante_producto g ON g.id_grupo_variante = pv.id_grupo_variante
    JOIN tab_productos p ON p.id_producto = g.id_producto AND p.ind_activo = TRUE
    WHERE cp.id_carrito = v_id_carrito;

    RETURN v_resultado;
END;
$$ LANGUAGE plpgsql;
