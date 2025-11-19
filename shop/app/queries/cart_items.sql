-- noinspection SqlInsertValuesForFile

-- name: get-cart-items-by-cart-id
SELECT ci.id,
       ci.cart_id,
       ci.product_id,
       p.title       AS product_title,
       ci.quantity
FROM cart_items ci
LEFT JOIN products p ON ci.product_id = p.id
WHERE ci.cart_id = :cart_id
ORDER BY ci.id;

-- name: get-cart-item-by-id^
SELECT id,
       cart_id,
       product_id,
       quantity
FROM cart_items
WHERE id = :id;

-- name: get-cart-item-by-cart-and-product^
SELECT id,
       cart_id,
       product_id,
       quantity
FROM cart_items
WHERE cart_id = :cart_id
  AND product_id = :product_id;

-- name: create-cart-item^
INSERT INTO cart_items (cart_id, product_id, quantity)
VALUES (:cart_id, :product_id, :quantity)
RETURNING id;

-- name: update-cart-item^
UPDATE cart_items
SET cart_id    = COALESCE(:cart_id, cart_id),
    product_id = COALESCE(:product_id, product_id),
    quantity   = COALESCE(:quantity, quantity)
WHERE id = :id
RETURNING id, cart_id, product_id, quantity;

-- name: delete-cart-item^
DELETE FROM cart_items
WHERE id = :id
RETURNING id;

-- name: delete-cart-items-by-cart-id
DELETE FROM cart_items
WHERE cart_id = :cart_id
RETURNING id;

