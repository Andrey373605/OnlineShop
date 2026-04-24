-- noinspection SqlInsertValuesForFile

-- name: get-all-products
SELECT p.id,
       p.title,
       p.description,
       p.price,
       p.stock,
       p.brand,
       p.thumbnail_key,
       p.is_published,
       p.category_id
FROM products p
ORDER BY p.id
LIMIT :limit OFFSET :offset;

-- name: get-products-count^
SELECT COUNT(*) as total FROM products p;

-- name: get-product-by-id^
SELECT p.id,
       p.title,
       p.description,
       p.price,
       p.stock,
       p.brand,
       p.thumbnail_key,
       p.is_published,
       p.category_id
FROM products p
WHERE p.id = :id;

-- name: create-product^
INSERT INTO products (title, description, price, stock, brand, thumbnail_key, is_published, category_id)
VALUES (:title, :description, :price, :stock, :brand, :thumbnail_key, :is_published, :category_id)
RETURNING id, title, description, price, stock, brand, thumbnail_key, is_published, category_id;

-- name: update-product^
UPDATE products
SET
    title         = COALESCE(:title, title),
    description   = COALESCE(:description, description),
    price         = COALESCE(:price, price),
    stock         = COALESCE(:stock, stock),
    brand         = COALESCE(:brand, brand),
    thumbnail_key = COALESCE(:thumbnail_key, thumbnail_key),
    is_published  = COALESCE(:is_published, is_published),
    category_id   = COALESCE(:category_id, category_id),
    updated_at    = NOW()
WHERE id = :id
RETURNING id, title, description, price, stock, brand, thumbnail_key, is_published, category_id;

-- name: delete-product^
DELETE FROM products
WHERE id = :id
RETURNING id;

-- name: check-product-id-exists^
SELECT EXISTS(SELECT 1 FROM products WHERE id = :id) as exists;
