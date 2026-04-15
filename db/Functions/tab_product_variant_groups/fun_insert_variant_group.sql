/*
 * Inserta un grupo de variante visual (ej. Color = Negro).
 * Un grupo = una galería de imágenes.
 */
CREATE OR REPLACE FUNCTION fun_insert_variant_group(
    p_product_id DECIMAL,
    p_dominant_attribute VARCHAR,
    p_dominant_value VARCHAR,
    p_is_active BOOLEAN DEFAULT TRUE
) RETURNS VARCHAR AS $$
DECLARE
    v_id BIGINT;
BEGIN
    IF p_product_id IS NULL OR NOT EXISTS (SELECT 1 FROM tab_productos WHERE id_producto = p_product_id) THEN
        RETURN 'Error: id_producto obligatorio y debe existir.';
    END IF;
    IF trim(p_dominant_attribute) = '' OR trim(p_dominant_value) = '' THEN
        RETURN 'Error: nom_atributo_dominante y valor_atributo_dominante obligatorios.';
    END IF;
    INSERT INTO tab_grupos_variante_producto (id_producto, nom_atributo_dominante, valor_atributo_dominante, ind_activo, usr_insert, fec_insert)
    VALUES (p_product_id, trim(p_dominant_attribute), trim(p_dominant_value), COALESCE(p_is_active, TRUE), 0, NOW())
    ON CONFLICT (id_producto, valor_atributo_dominante) DO UPDATE SET
        ind_activo = EXCLUDED.ind_activo,
        fec_update = NOW()
    RETURNING id_grupo_variante INTO v_id;
    RETURN 'OK:' || v_id;
EXCEPTION
    WHEN OTHERS THEN RETURN 'Error: ' || SQLERRM;
END;
$$ LANGUAGE plpgsql;
