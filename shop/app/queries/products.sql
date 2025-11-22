-- noinspection SqlInsertValuesForFile

-- name: get-all-products
SELECT p.id,
       p.title,
       p.description,
       p.price,
       p.stock,
       p.brand,
       p.thumbnail_url,
       p.is_published,
       p.created_at,
       c.id as category_id,
       c.name as category_name
FROM products p
LEFT JOIN categories c ON p.category_id = c.id
ORDER BY p.id
LIMIT :limit OFFSET :offset;

-- name: get-products-count
SELECT COUNT(*) as total FROM products p;

-- name: get-product-by-id^
SELECT p.id,
       p.title,
       p.description,
       p.price,
       p.stock,
       p.brand,
       p.thumbnail_url,
       p.is_published,
       p.created_at,
       p.updated_at,
       c.id as category_id,
       c.name as categoty_name,
       COALESCE(
            (SELECT json_agg(json_build_object('id', pi.id, 'path', pi.image_path))
             FROM product_images pi
             WHERE pi.product_id = p.id),
            '[]'
       ) AS images
FROM products p
LEFT JOIN categories c ON p.category_id = c.id
WHERE p.id = :id;

-- name: create-product^
INSERT INTO products (title, description, price, stock, brand, thumbnail_url, is_published, category_id)
VALUES (:title, :description, :price, :stock, :brand, :thumbnail_url, :is_published, :category_id)
RETURNING id;

-- name: update-product^
UPDATE products
SET
    title         = COALESCE(:title, title),
    description   = COALESCE(:description, description),
    price         = COALESCE(:price, price),
    stock         = COALESCE(:stock, stock),
    brand         = COALESCE(:brand, brand),
    thumbnail_url = COALESCE(:thumbnail_url, thumbnail_url),
    is_published  = COALESCE(:is_published, is_published),
    category_id   = COALESCE(:category_id, category_id),
    updated_at    = NOW()
WHERE id = :id
RETURNING id;

-- name: delete-product^
DELETE FROM products
WHERE id = :id
RETURNING id;

-- name: check-product-id-exists^
SELECT EXISTS(SELECT 1 FROM products WHERE id = :id) as exists;
