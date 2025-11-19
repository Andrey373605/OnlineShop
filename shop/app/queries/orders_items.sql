-- noinspection SqlInsertValuesForFile

-- name: get-order-items-by-order-id
SELECT oi.id,
       oi.order_id,
       oi.product_id,
       p.title AS product_title,
       oi.quantity,
       oi.unit_price
FROM orders_items oi
LEFT JOIN products p ON oi.product_id = p.id
WHERE oi.order_id = :order_id
ORDER BY oi.id;

-- name: get-order-item-by-id^
SELECT id,
       order_id,
       product_id,
       quantity,
       unit_price
FROM orders_items
WHERE id = :id;

-- name: create-order-item^
INSERT INTO orders_items (order_id, product_id, quantity, unit_price)
VALUES (:order_id, :product_id, :quantity, :unit_price)
RETURNING id;

-- name: update-order-item^
UPDATE orders_items
SET order_id   = COALESCE(:order_id, order_id),
    product_id = COALESCE(:product_id, product_id),
    quantity   = COALESCE(:quantity, quantity),
    unit_price = COALESCE(:unit_price, unit_price)
WHERE id = :id
RETURNING id, order_id, product_id, quantity, unit_price;

-- name: delete-order-item^
DELETE FROM orders_items
WHERE id = :id
RETURNING id;

-- name: delete-order-items-by-order-id
DELETE FROM orders_items
WHERE order_id = :order_id
RETURNING id;

