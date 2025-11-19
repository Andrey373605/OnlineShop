-- noinspection SqlInsertValuesForFile

-- name: get-product-images-by-product-id
SELECT id,
       product_id,
       image_path
FROM product_images
WHERE product_id = :product_id
ORDER BY id;

-- name: get-product-image-by-id^
SELECT id,
       product_id,
       image_path
FROM product_images
WHERE id = :id;

-- name: create-product-image^
INSERT INTO product_images (product_id, image_path)
VALUES (:product_id, :image_path)
RETURNING id;

-- name: update-product-image^
UPDATE product_images
SET product_id = COALESCE(:product_id, product_id),
    image_path = COALESCE(:image_path, image_path)
WHERE id = :id
RETURNING id, product_id, image_path;

-- name: delete-product-image^
DELETE FROM product_images
WHERE id = :id
RETURNING id;

-- name: delete-product-images-by-product-id
DELETE FROM product_images
WHERE product_id = :product_id
RETURNING id;

