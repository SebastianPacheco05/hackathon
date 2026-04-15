-- Añade id_proveedor a tab_productos para asociar producto a proveedor (opcional).
-- Debe ejecutarse después de que existan tab_productos y tab_proveedores.

ALTER TABLE tab_productos
  ADD COLUMN IF NOT EXISTS id_proveedor DECIMAL(10) NULL REFERENCES tab_proveedores(id_proveedor);

CREATE INDEX IF NOT EXISTS idx_tab_productos_id_proveedor ON tab_productos(id_proveedor);

COMMENT ON COLUMN tab_productos.id_proveedor IS 'Proveedor del producto; opcional.';
