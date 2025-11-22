-- noinspection SqlInsertValuesForFile

-- name: get-all-reviews
SELECT r.id,
       r.user_id,
       u.username,
       r.product_id,
       p.title AS product_title,
       r.title,
       r.description,
       r.rating,
       r.created_at,
       r.updated_at
FROM reviews r
LEFT JOIN users u ON r.user_id = u.id
LEFT JOIN products p ON r.product_id = p.id
ORDER BY r.id
LIMIT :limit OFFSET :offset;

-- name: get-review-by-id^
SELECT r.id,
       r.user_id,
       u.username,
       r.product_id,
       p.title AS product_title,
       r.title,
       r.description,
       r.rating,
       r.created_at,
       r.updated_at
FROM reviews r
LEFT JOIN users u ON r.user_id = u.id
LEFT JOIN products p ON r.product_id = p.id
WHERE r.id = :id;

-- name: get-review-by-user-and-product^
SELECT r.id,
       r.user_id,
       u.username,
       r.product_id,
       p.title AS product_title,
       r.title,
       r.description,
       r.rating,
       r.created_at,
       r.updated_at
FROM reviews r
LEFT JOIN users u ON r.user_id = u.id
LEFT JOIN products p ON r.product_id = p.id
WHERE r.user_id = :user_id
  AND r.product_id = :product_id;

-- name: create-review^
INSERT INTO reviews (user_id, product_id, title, description, rating)
VALUES (:user_id, :product_id, :title, :description, :rating)
RETURNING id;

-- name: update-review^
UPDATE reviews
SET title       = COALESCE(:title, title),
    description = COALESCE(:description, description),
    rating      = COALESCE(:rating, rating),
    updated_at  = NOW()
WHERE id = :id
RETURNING id, user_id, product_id, rating;

-- name: delete-review^
DELETE FROM reviews
WHERE id = :id
RETURNING id;

