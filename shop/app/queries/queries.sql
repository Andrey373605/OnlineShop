UPDATE products
SET title = 'telephone'
WHERE id > 5;

DELETE FROM products
WHERE id = 8;

SELECT * FROM products
JOIN categories ON products.category_id = categories.id;


SELECT username, r.name, users.created_at FROM event_log
JOIN users ON event_log.user_id = users.id
JOIN roles r ON users.role = r.id
WHERE event_log.event_type = 'AUTH_LOGIN';


SELECT p.id, p.title
FROM products p
WHERE EXISTS(
      SELECT 1
     FROM cart_items ci
    WHERE ci.product_id = p.id
      )
AND NOT EXISTS (
    SELECT 1
    FROM orders_items oi
    WHERE oi.product_id = p.id
);

SELECT *
FROM products;

SELECT *
FROM cart_items;

SELECT *
FROM orders_items;
