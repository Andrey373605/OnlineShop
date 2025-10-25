-- noinspection SqlInsertValuesForFile

-- name: get-by-product-specification-by-id
SELECT *
FROM product_specifications;

-- name: get-by-product-specification-by-product-id
SELECT *
FROM product_specifications
WHERE id = :id;