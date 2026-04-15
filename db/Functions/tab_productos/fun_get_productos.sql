/*
 * Lista productos con categoría, precio mínimo, cant_stock total e imagen principal.
 * Usa tab_productos, variant_combinations/groups, variant_images, tab_categorias.
 */
CREATE OR REPLACE FUNCTION fun_get_productos()
RETURNS TABLE (
    id_producto DECIMAL,
    id_categoria DECIMAL,
    nom_categoria VARCHAR,
    nom_producto VARCHAR,
    slug_producto VARCHAR,
    descripcion TEXT,
    id_marca DECIMAL,
    ind_activo BOOLEAN,
    precio_min DECIMAL,
    stock_total BIGINT,
    img_principal VARCHAR
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        p.id_producto AS id_producto,
        p.id_categoria,
        c.nom_categoria AS nom_categoria,
        p.nom_producto AS nom_producto,
        p.slug_producto AS slug_producto,
        p.descripcion,
        p.id_marca,
        p.ind_activo,
        (SELECT MIN(cmb.precio) FROM tab_combinaciones_variante_producto cmb JOIN tab_grupos_variante_producto g ON g.id_grupo_variante = cmb.id_grupo_variante WHERE g.id_producto = p.id_producto AND cmb.ind_activo = TRUE) AS precio_min,
        (SELECT COALESCE(SUM(cmb.cant_stock), 0) FROM tab_combinaciones_variante_producto cmb JOIN tab_grupos_variante_producto g ON g.id_grupo_variante = cmb.id_grupo_variante WHERE g.id_producto = p.id_producto AND cmb.ind_activo = TRUE) AS stock_total,
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
        ) AS img_principal
    FROM tab_productos p
    JOIN tab_categorias c ON c.id_categoria = p.id_categoria
    ORDER BY p.id_producto;
END;
$$ LANGUAGE plpgsql;
