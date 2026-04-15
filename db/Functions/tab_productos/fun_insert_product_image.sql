/*
 * Inserta una imagen usando el modelo variant_groups + tab_imagenes_grupo_variante.
 * p_variant_id NULL = imagen del producto (grupo "Sin color"); p_variant_id NOT NULL = grupo de esa combinación.
 */
CREATE OR REPLACE FUNCTION fun_insert_product_image(
    p_product_id DECIMAL,
    p_image_url VARCHAR,
    p_is_main BOOLEAN DEFAULT FALSE,
    p_sort_order INT DEFAULT 0,
    p_usr_operacion DECIMAL(10) DEFAULT NULL,
    p_variant_id DECIMAL DEFAULT NULL
) RETURNS VARCHAR AS $$
DECLARE
    v_id BIGINT;
    v_group_id BIGINT;
BEGIN
    IF p_product_id IS NULL OR NOT EXISTS (SELECT 1 FROM tab_productos WHERE id_producto = p_product_id) THEN
        RETURN 'Error: id_producto obligatorio y debe existir.';
    END IF;
    IF p_image_url IS NULL OR trim(p_image_url) = '' THEN
        RETURN 'Error: url_imagen obligatorio.';
    END IF;

    IF p_variant_id IS NOT NULL THEN
        SELECT id_grupo_variante INTO v_group_id FROM tab_combinaciones_variante_producto WHERE id_combinacion_variante = p_variant_id LIMIT 1;
        IF v_group_id IS NULL THEN
            RETURN 'Error: id_combinacion_variante (combination) no existe.';
        END IF;
        IF NOT EXISTS (SELECT 1 FROM tab_grupos_variante_producto WHERE id_grupo_variante = v_group_id AND id_producto = p_product_id) THEN
            RETURN 'Error: la combinación no pertenece al producto.';
        END IF;
    ELSE
        SELECT id_grupo_variante INTO v_group_id FROM tab_grupos_variante_producto WHERE id_producto = p_product_id AND valor_atributo_dominante = 'Sin color' LIMIT 1;
        IF v_group_id IS NULL THEN
            INSERT INTO tab_grupos_variante_producto (id_producto, nom_atributo_dominante, valor_atributo_dominante, ind_activo, usr_insert, fec_insert)
            VALUES (p_product_id, 'color', 'Sin color', TRUE, COALESCE(p_usr_operacion, 0), NOW())
            RETURNING id_grupo_variante INTO v_group_id;
        END IF;
    END IF;

    IF p_is_main THEN
        UPDATE tab_imagenes_grupo_variante SET ind_principal = FALSE WHERE id_grupo_variante = v_group_id;
    END IF;

    INSERT INTO tab_imagenes_grupo_variante (id_grupo_variante, url_imagen, ind_principal, orden, usr_insert, fec_insert)
    VALUES (v_group_id, trim(p_image_url), COALESCE(p_is_main, FALSE), COALESCE(p_sort_order, 0), COALESCE(p_usr_operacion, 0), NOW())
    RETURNING id_imagen_grupo_variante INTO v_id;
    RETURN 'OK:' || v_id;
EXCEPTION
    WHEN OTHERS THEN RETURN 'Error: ' || SQLERRM;
END;
$$ LANGUAGE plpgsql;
