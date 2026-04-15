/*
 * Inserta una variante usando el modelo variant_groups/combinations.
 * Crea un grupo "Sin color" si no existe y una combinación con el precio/cant_stock/SKU indicados.
 * Compatible con el path de creación simple (un producto, una variante).
 */
CREATE OR REPLACE FUNCTION fun_insert_product_variant(
    p_product_id DECIMAL,
    p_price DECIMAL(12,2),
    p_stock INT DEFAULT 0,
    p_sku VARCHAR DEFAULT NULL,
    p_is_active BOOLEAN DEFAULT TRUE,
    p_usr_operacion DECIMAL(10) DEFAULT NULL
) RETURNS VARCHAR AS $$
DECLARE
    v_group_id BIGINT;
    v_id DECIMAL(10);
    v_sku VARCHAR;
    v_usr DECIMAL(10);
BEGIN
    v_usr := COALESCE(p_usr_operacion, 0);
    IF p_product_id IS NULL OR NOT EXISTS (SELECT 1 FROM tab_productos WHERE id_producto = p_product_id) THEN
        RETURN 'Error: id_producto obligatorio y debe existir.';
    END IF;
    IF p_price IS NULL OR p_price < 0 THEN
        RETURN 'Error: precio obligatorio y >= 0.';
    END IF;
    IF p_stock IS NULL OR p_stock < 0 THEN
        RETURN 'Error: cant_stock debe ser >= 0.';
    END IF;

    INSERT INTO tab_grupos_variante_producto (id_producto, nom_atributo_dominante, valor_atributo_dominante, ind_activo, usr_insert, fec_insert)
    VALUES (p_product_id, 'color', 'Sin color', TRUE, v_usr, NOW())
    ON CONFLICT (id_producto, valor_atributo_dominante) DO UPDATE SET ind_activo = TRUE, fec_update = NOW()
    RETURNING id_grupo_variante INTO v_group_id;
    IF v_group_id IS NULL THEN
        SELECT id_grupo_variante INTO v_group_id FROM tab_grupos_variante_producto WHERE id_producto = p_product_id AND valor_atributo_dominante = 'Sin color' LIMIT 1;
    END IF;

    v_sku := fun_generate_sku(p_product_id, nullif(trim(p_sku), ''));
    IF length(v_sku) >= 120 THEN
        RETURN 'Error: SKU no debe superar 119 caracteres.';
    END IF;

    v_id := (SELECT COALESCE(MAX(id_combinacion_variante), 0) + 1 FROM tab_combinaciones_variante_producto);
    INSERT INTO tab_combinaciones_variante_producto (id_combinacion_variante, id_grupo_variante, cod_sku, precio, cant_stock, atributos, ind_activo, usr_insert, fec_insert)
    VALUES (v_id, v_group_id, v_sku, p_price, COALESCE(p_stock, 0), '{}'::JSONB, COALESCE(p_is_active, TRUE), v_usr, NOW());

    RETURN 'OK:' || v_id;
EXCEPTION
    WHEN unique_violation THEN RETURN 'Error: SKU duplicado.';
    WHEN OTHERS THEN RETURN 'Error: ' || SQLERRM;
END;
$$ LANGUAGE plpgsql;
