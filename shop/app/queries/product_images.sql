-- noinspection SqlInsertValuesForFile

-- name: get-product-images-by-product-id
SELECT id,
       product_id,
       storage_key
FROM product_images
WHERE product_id = :product_id
ORDER BY id;

-- name: get-product-image-by-id^
SELECT id,
       product_id,
       storage_key
FROM product_images
WHERE id = :id;

-- name: create-product-image^
INSERT INTO product_images (product_id, storage_key)
VALUES (:product_id, :storage_key)
RETURNING id;

-- name: update-product-image^
UPDATE product_images
SET product_id = COALESCE(:product_id, product_id),
    storage_key = COALESCE(:storage_key, storage_key)
WHERE id = :id
RETURNING id, product_id, storage_key;

-- name: delete-product-image^
DELETE FROM product_images
WHERE id = :id
RETURNING id;

-- name: delete-product-images-by-product-id
DELETE FROM product_images
WHERE product_id = :product_id
RETURNING id;

