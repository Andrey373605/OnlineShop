-- noinspection SqlInsertValuesForFile

-- name: get-all-carts
SELECT c.id,
       c.user_id,
       u.username,
       c.created_at,
       c.total_amount
FROM carts c
LEFT JOIN users u ON c.user_id = u.id
ORDER BY c.id
LIMIT :limit OFFSET :offset;

-- name: get-cart-by-id^
SELECT c.id,
       c.user_id,
       u.username,
       c.created_at,
       c.total_amount
FROM carts c
LEFT JOIN users u ON c.user_id = u.id
WHERE c.id = :id;

-- name: get-cart-by-user-id^
SELECT c.id,
       c.user_id,
       c.created_at,
       c.total_amount
FROM carts c
WHERE c.user_id = :user_id;

-- name: create-cart^
INSERT INTO carts (user_id, total_amount)
VALUES (:user_id, COALESCE(:total_amount, 0.0))
RETURNING id;

-- name: update-cart^
UPDATE carts
SET user_id     = COALESCE(:user_id, user_id),
    total_amount = COALESCE(:total_amount, total_amount)
WHERE id = :id
RETURNING id, user_id, total_amount;

-- name: delete-cart^
DELETE FROM carts
WHERE id = :id
RETURNING id;

