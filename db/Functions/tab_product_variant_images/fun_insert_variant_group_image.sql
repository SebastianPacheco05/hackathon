/*
 * Inserta una imagen en un grupo de variante (tab_imagenes_grupo_variante).
 * ind_principal: si TRUE, se puede desmarcar ind_principal en otras del mismo grupo.
 */
CREATE OR REPLACE FUNCTION fun_insert_variant_group_image(
    p_variant_group_id BIGINT,
    p_image_url VARCHAR,
    p_is_primary BOOLEAN DEFAULT FALSE,
    p_sort_order INT DEFAULT 0
) RETURNS VARCHAR AS $$
DECLARE
    v_id BIGINT;
BEGIN
    IF p_variant_group_id IS NULL OR NOT EXISTS (SELECT 1 FROM tab_grupos_variante_producto WHERE id_grupo_variante = p_variant_group_id) THEN
        RETURN 'Error: id_grupo_variante obligatorio y debe existir.';
    END IF;
    IF p_image_url IS NULL OR trim(p_image_url) = '' THEN
        RETURN 'Error: url_imagen obligatorio.';
    END IF;
    IF p_is_primary THEN
        UPDATE tab_imagenes_grupo_variante SET ind_principal = FALSE WHERE id_grupo_variante = p_variant_group_id;
    END IF;
    INSERT INTO tab_imagenes_grupo_variante (id_grupo_variante, url_imagen, ind_principal, orden, usr_insert, fec_insert)
    VALUES (p_variant_group_id, trim(p_image_url), COALESCE(p_is_primary, FALSE), COALESCE(p_sort_order, 0), 0, NOW())
    RETURNING id_imagen_grupo_variante INTO v_id;
    RETURN 'OK:' || v_id;
EXCEPTION
    WHEN OTHERS THEN RETURN 'Error: ' || SQLERRM;
END;
$$ LANGUAGE plpgsql;
