-- noinspection SqlInsertValuesForFile

-- name: get-all-product-specifications
SELECT id,
       product_id,
       specifications,
       created_at,
       updated_at
FROM product_specifications
ORDER BY id;

-- name: get-product-specification-by-id^
SELECT id,
       product_id,
       specifications,
       created_at,
       updated_at
FROM product_specifications
WHERE id = :id;

-- name: get-product-specification-by-product-id^
SELECT id,
       product_id,
       specifications,
       created_at,
       updated_at
FROM product_specifications
WHERE product_id = :product_id;

-- name: create-product-specification^
INSERT INTO product_specifications (product_id, specifications)
VALUES (:product_id, COALESCE(:specifications::jsonb, '{}'::jsonb))
RETURNING id;

-- name: update-product-specification^
UPDATE product_specifications
SET product_id     = COALESCE(:product_id, product_id),
    specifications = COALESCE(:specifications::jsonb, specifications),
    updated_at     = NOW()
WHERE id = :id
RETURNING id, product_id, specifications;

-- name: delete-product-specification^
DELETE FROM product_specifications
WHERE id = :id
RETURNING id;