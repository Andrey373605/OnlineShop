-- noinspection SqlInsertValuesForFile

-- name: get-all-orders
SELECT o.id,
       o.user_id,
       u.username,
       o.order_number,
       o.status,
       o.total_amount,
       o.shipping_address,
       o.payment_method,
       o.payment_status,
       o.created_at
FROM orders o
LEFT JOIN users u ON o.user_id = u.id
ORDER BY o.created_at DESC
LIMIT :limit OFFSET :offset;

-- name: get-orders-count
SELECT COUNT(*) AS total
FROM orders;

-- name: get-order-by-id^
SELECT o.id,
       o.user_id,
       o.order_number,
       o.status,
       o.total_amount,
       o.shipping_address,
       o.payment_method,
       o.payment_status,
       o.created_at
FROM orders o
WHERE o.id = :id;

-- name: get-order-by-number^
SELECT o.id,
       o.user_id,
       o.order_number,
       o.status,
       o.total_amount,
       o.shipping_address,
       o.payment_method,
       o.payment_status,
       o.created_at
FROM orders o
WHERE o.order_number = :order_number;

-- name: create-order^
INSERT INTO orders (user_id,
                    order_number,
                    status,
                    total_amount,
                    shipping_address,
                    payment_method,
                    payment_status)
VALUES (:user_id,
        :order_number,
        :status,
        :total_amount,
        :shipping_address,
        :payment_method,
        :payment_status)
RETURNING id;

-- name: update-order^
UPDATE orders
SET status           = COALESCE(:status, status),
    total_amount     = COALESCE(:total_amount, total_amount),
    shipping_address = COALESCE(:shipping_address, shipping_address),
    payment_method   = COALESCE(:payment_method, payment_method),
    payment_status   = COALESCE(:payment_status, payment_status)
WHERE id = :id
RETURNING id, status, total_amount;

-- name: delete-order^
DELETE FROM orders
WHERE id = :id
RETURNING id;

