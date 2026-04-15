/*
 * Lista todos los productos (activos e inactivos) para el panel de administración.
 * Usa tab_productos, variant_combinations/groups, variant_images, tab_categorias, tab_marcas.
 *
 * Si la función ya existe y cambias el tipo de retorno (ej. añadir precio_max),
 * PostgreSQL exige DROP antes de CREATE. Ejecuta primero:
 *   DROP FUNCTION IF EXISTS fun_get_all_products_admin(varchar, varchar, int, int);
 */
DROP FUNCTION IF EXISTS fun_get_all_products_admin(varchar, varchar, int, int);

CREATE OR REPLACE FUNCTION fun_get_all_products_admin(
    p_ordenar_por VARCHAR(20) DEFAULT 'nombre',
    p_orden VARCHAR(4) DEFAULT 'ASC',
    p_limit INT DEFAULT 50,
    p_offset INT DEFAULT 0
)
RETURNS TABLE (
    id_producto DECIMAL,
    id_categoria DECIMAL,
    nom_categoria VARCHAR,
    nom_producto VARCHAR,
    slug_producto VARCHAR,
    descripcion TEXT,
    img_principal VARCHAR,
    precio_min DECIMAL,
    precio_max DECIMAL,
    stock_total BIGINT,
    id_marca DECIMAL,
    nom_marca VARCHAR,
    id_proveedor DECIMAL,
    nom_proveedor VARCHAR,
    fec_insert TIMESTAMP WITHOUT TIME ZONE,
    ind_activo_producto BOOLEAN,
    ind_activo_categoria BOOLEAN,
    ind_activo_marca BOOLEAN,
    total_registros BIGINT
) AS $$
BEGIN
    IF p_limit > 1000 THEN p_limit := 1000; END IF;
    IF p_offset < 0 THEN p_offset := 0; END IF;
    IF UPPER(p_orden) NOT IN ('ASC', 'DESC') THEN p_orden := 'ASC'; END IF;
    IF p_ordenar_por NOT IN ('precio', 'nombre', 'cant_stock', 'fecha', 'categoria', 'marca') THEN
        p_ordenar_por := 'nombre';
    END IF;

    RETURN QUERY
    WITH agg AS (
        SELECT
            p.id_producto AS id_producto,
            p.id_categoria,
            cat.nom_categoria AS nom_categoria,
            p.nom_producto AS nom_producto,
            p.slug_producto AS slug_producto,
            p.descripcion,
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
            -- Para admin: mostrar precio y cant_stock incluso si las variantes están inactivas
            (SELECT MIN(cmb.precio) FROM tab_combinaciones_variante_producto cmb JOIN tab_grupos_variante_producto g ON g.id_grupo_variante = cmb.id_grupo_variante WHERE g.id_producto = p.id_producto) AS precio_min,
            (SELECT MAX(cmb.precio) FROM tab_combinaciones_variante_producto cmb JOIN tab_grupos_variante_producto g ON g.id_grupo_variante = cmb.id_grupo_variante WHERE g.id_producto = p.id_producto) AS precio_max,
            (SELECT COALESCE(SUM(cmb.cant_stock), 0) FROM tab_combinaciones_variante_producto cmb JOIN tab_grupos_variante_producto g ON g.id_grupo_variante = cmb.id_grupo_variante WHERE g.id_producto = p.id_producto) AS stock_total,
            p.id_marca,
            m.nom_marca,
            p.id_proveedor,
            pr.nom_proveedor,
            p.fec_insert,
            p.ind_activo AS ind_activo_producto,
            cat.ind_activo AS ind_activo_categoria,
            m.ind_activo AS ind_activo_marca
        FROM tab_productos p
        JOIN tab_categorias cat ON cat.id_categoria = p.id_categoria
        LEFT JOIN tab_marcas m ON m.id_marca = p.id_marca
        LEFT JOIN tab_proveedores pr ON pr.id_proveedor = p.id_proveedor
    ),
    total AS (SELECT COUNT(1) AS n FROM agg)
    SELECT
        a.id_producto,
        a.id_categoria,
        a.nom_categoria,
        a.nom_producto,
        a.slug_producto,
        a.descripcion,
        a.img_principal,
        a.precio_min,
        a.precio_max,
        a.stock_total::BIGINT,
        a.id_marca,
        a.nom_marca,
        a.id_proveedor,
        a.nom_proveedor,
        a.fec_insert,
        a.ind_activo_producto,
        a.ind_activo_categoria,
        a.ind_activo_marca,
        (SELECT n FROM total)
    FROM agg a
    ORDER BY
        CASE WHEN p_ordenar_por = 'precio' AND UPPER(p_orden) = 'ASC' THEN a.precio_min END ASC NULLS LAST,
        CASE WHEN p_ordenar_por = 'precio' AND UPPER(p_orden) = 'DESC' THEN a.precio_min END DESC NULLS LAST,
        CASE WHEN p_ordenar_por = 'nombre' AND UPPER(p_orden) = 'ASC' THEN a.nom_producto END ASC,
        CASE WHEN p_ordenar_por = 'nombre' AND UPPER(p_orden) = 'DESC' THEN a.nom_producto END DESC,
        CASE WHEN p_ordenar_por = 'cant_stock' AND UPPER(p_orden) = 'ASC' THEN a.stock_total END ASC NULLS LAST,
        CASE WHEN p_ordenar_por = 'cant_stock' AND UPPER(p_orden) = 'DESC' THEN a.stock_total END DESC NULLS LAST,
        CASE WHEN p_ordenar_por = 'fecha' AND UPPER(p_orden) = 'ASC' THEN a.fec_insert END ASC NULLS LAST,
        CASE WHEN p_ordenar_por = 'fecha' AND UPPER(p_orden) = 'DESC' THEN a.fec_insert END DESC NULLS LAST,
        CASE WHEN p_ordenar_por = 'categoria' AND UPPER(p_orden) = 'ASC' THEN a.nom_categoria END ASC,
        CASE WHEN p_ordenar_por = 'categoria' AND UPPER(p_orden) = 'DESC' THEN a.nom_categoria END DESC,
        CASE WHEN p_ordenar_por = 'marca' AND UPPER(p_orden) = 'ASC' THEN a.nom_marca END ASC NULLS LAST,
        CASE WHEN p_ordenar_por = 'marca' AND UPPER(p_orden) = 'DESC' THEN a.nom_marca END DESC NULLS LAST,
        a.id_producto
    LIMIT p_limit OFFSET p_offset;
EXCEPTION
    WHEN OTHERS THEN
        RAISE EXCEPTION 'Error en obtención de productos para admin: %', SQLERRM;
END;
$$ LANGUAGE plpgsql;
