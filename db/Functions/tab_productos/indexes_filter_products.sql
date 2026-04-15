/*
 * Índices para optimizar fun_filter_products (tab_productos, combinaciones/grupos, tab_categorias).
 */
-- productos: categoría, marca, nombre, activo
CREATE INDEX IF NOT EXISTS idx_productos_categoria_activo ON tab_productos (id_categoria, ind_activo) WHERE ind_activo = TRUE;
CREATE INDEX IF NOT EXISTS idx_productos_marca_activo ON tab_productos (id_marca, ind_activo) WHERE ind_activo = TRUE;
CREATE INDEX IF NOT EXISTS idx_productos_nombre ON tab_productos (nom_producto) WHERE ind_activo = TRUE;
CREATE INDEX IF NOT EXISTS idx_productos_categoria_marca ON tab_productos (id_categoria, id_marca, ind_activo) WHERE ind_activo = TRUE;
-- categories
CREATE INDEX IF NOT EXISTS idx_categorias_activa ON tab_categorias (id_categoria, id_categoria_padre) WHERE ind_activo = TRUE;
-- Actualizar estadísticas
ANALYZE tab_productos;
ANALYZE tab_categorias;
ANALYZE tab_combinaciones_variante_producto;
ANALYZE tab_grupos_variante_producto;
