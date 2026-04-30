-- Phase C: commerce snapshots + shop sync cursors + composite uniqueness per shop

ALTER TABLE shops ADD COLUMN IF NOT EXISTS product_sync_cursor text;
ALTER TABLE shops ADD COLUMN IF NOT EXISTS order_sync_cursor text;

ALTER TABLE products ADD COLUMN IF NOT EXISTS api_snapshot_json jsonb;
ALTER TABLE orders ADD COLUMN IF NOT EXISTS api_snapshot_json jsonb;

ALTER TABLE products DROP CONSTRAINT IF EXISTS products_platform_product_id_unique;
ALTER TABLE products DROP CONSTRAINT IF EXISTS products_platform_product_id_key;
DO $$
BEGIN
  ALTER TABLE products ADD CONSTRAINT uq_products_shop_platform UNIQUE (shop_id, platform_product_id);
EXCEPTION WHEN duplicate_object THEN NULL;
END $$;

ALTER TABLE orders DROP CONSTRAINT IF EXISTS orders_platform_order_id_unique;
ALTER TABLE orders DROP CONSTRAINT IF EXISTS orders_platform_order_id_key;
DO $$
BEGIN
  ALTER TABLE orders ADD CONSTRAINT uq_orders_shop_platform UNIQUE (shop_id, platform_order_id);
EXCEPTION WHEN duplicate_object THEN NULL;
END $$;
