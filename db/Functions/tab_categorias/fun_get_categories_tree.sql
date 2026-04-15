/*
 * Devuelve categorías en estructura de árbol (lista plana con id_categoria_padre y level).
 * p_root_id NULL = todas; si se pasa un id, solo esa categoría y sus descendientes.
 * p_active_only: si TRUE, solo ind_activo = TRUE.
 */
DROP FUNCTION IF EXISTS fun_get_categories_tree(DECIMAL, BOOLEAN);

CREATE OR REPLACE FUNCTION fun_get_categories_tree(
    p_root_id DECIMAL DEFAULT NULL,
    p_active_only BOOLEAN DEFAULT FALSE
)
RETURNS TABLE (
    id DECIMAL,
    name VARCHAR,
    slug VARCHAR,
    parent_id DECIMAL,
    is_active BOOLEAN,
    level INT,
    path_ids DECIMAL[]
) AS $$
BEGIN
    RETURN QUERY
    WITH RECURSIVE tree AS (
        SELECT c.id_categoria, c.nom_categoria, c.slug_categoria, c.id_categoria_padre, c.ind_activo,
               0 AS level,
               ARRAY[c.id_categoria]::DECIMAL[] AS path_ids
        FROM tab_categorias c
        WHERE (p_root_id IS NULL AND c.id_categoria_padre IS NULL)
           OR (p_root_id IS NOT NULL AND c.id_categoria = p_root_id)
        AND (NOT p_active_only OR c.ind_activo = TRUE)
        UNION ALL
        SELECT c.id_categoria, c.nom_categoria, c.slug_categoria, c.id_categoria_padre, c.ind_activo,
               t.level + 1,
               t.path_ids || c.id_categoria
        FROM tab_categorias c
        INNER JOIN tree t ON c.id_categoria_padre = t.id_categoria
        WHERE (NOT p_active_only OR c.ind_activo = TRUE)
    )
    SELECT t.id_categoria AS id, t.nom_categoria AS name, t.slug_categoria AS slug, t.id_categoria_padre AS parent_id, t.ind_activo AS is_active, t.level, t.path_ids
    FROM tree t
    ORDER BY t.path_ids;
END;
$$ LANGUAGE plpgsql;
