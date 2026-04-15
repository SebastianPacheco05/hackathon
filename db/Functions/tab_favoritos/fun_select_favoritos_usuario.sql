/*
 * Lista favoritos del usuario con detalle: id_producto, nombre, imagen principal, precio mínimo.
 * Usa tab_favoritos.id_producto y tablas products, variant_combinations/groups, variant_images.
 */
CREATE OR REPLACE FUNCTION fun_select_favoritos_usuario_con_detalles(
    p_id_usuario tab_favoritos.id_usuario%TYPE
) RETURNS TABLE (
    id_usuario DECIMAL,
    id_producto DECIMAL,
    fec_insert TIMESTAMP,
    nom_producto VARCHAR,
    img_principal VARCHAR,
    precio_min DECIMAL
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        tf.id_usuario,
        tf.id_producto,
        tf.fec_insert,
        p.nom_producto AS nom_producto,
        COALESCE(
          (SELECT pvi.url_imagen FROM tab_imagenes_grupo_variante pvi
           INNER JOIN tab_grupos_variante_producto g ON g.id_grupo_variante = pvi.id_grupo_variante
           WHERE g.id_producto = p.id_producto
             AND LOWER(TRIM(COALESCE(g.valor_atributo_dominante, ''))) = 'sin color'
           ORDER BY pvi.ind_principal DESC NULLS LAST, pvi.orden NULLS LAST, pvi.id_imagen_grupo_variante
           LIMIT 1),
          (SELECT pvi.url_imagen FROM tab_imagenes_grupo_variante pvi
           INNER JOIN tab_grupos_variante_producto g ON g.id_grupo_variante = pvi.id_grupo_variante
           WHERE g.id_producto = p.id_producto
           ORDER BY g.id_grupo_variante, pvi.orden, pvi.id_imagen_grupo_variante
           LIMIT 1)
        ) AS img_principal,
        (SELECT MIN(cmb.precio) FROM tab_combinaciones_variante_producto cmb JOIN tab_grupos_variante_producto g ON g.id_grupo_variante = cmb.id_grupo_variante WHERE g.id_producto = p.id_producto AND cmb.ind_activo = TRUE) AS precio_min
    FROM tab_favoritos tf
    JOIN tab_productos p ON p.id_producto = tf.id_producto
    WHERE tf.id_usuario = p_id_usuario
    ORDER BY tf.fec_insert DESC;
END;
$$ LANGUAGE plpgsql;

-- Alias para compatibilidad
CREATE OR REPLACE FUNCTION fun_select_favoritos_usuario(p_id_usuario tab_favoritos.id_usuario%TYPE)
RETURNS TABLE (
    id_usuario DECIMAL,
    id_producto DECIMAL,
    fec_insert TIMESTAMP,
    nom_producto VARCHAR,
    img_principal VARCHAR,
    precio_min DECIMAL
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        id_usuario,
        id_producto,
        fec_insert,
        nom_producto,
        img_principal,
        precio_min
    FROM fun_select_favoritos_usuario_con_detalles(p_id_usuario);
END;
$$ LANGUAGE plpgsql;
