-- noinspection SqlInsertValuesForFile

-- name: get-all-categories
SELECT id, name
FROM categories;

-- name: get-category-by-id
SELECT id, name
FROM categories
WHERE id = :id;

-- name: create-category^
INSERT INTO categories (name)
VALUES (:name)
RETURNING id;

-- name: update-category^
UPDATE categories
SET name = :name
WHERE id = :id
RETURNING id, name;

-- name: delete-category^
DELETE FROM categories
WHERE id = :id
RETURNING id