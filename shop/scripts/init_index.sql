-- Индексы для таблицы users
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_role_active ON users(role, is_active);

-- Индексы для таблицы products
CREATE INDEX idx_products_category_published ON products(category_id, is_published);
CREATE INDEX idx_products_price_stock ON products(price, stock);
CREATE INDEX idx_products_created_at ON products(created_at);

-- Индексы для таблицы reviews
CREATE INDEX idx_reviews_product_rating ON reviews(product_id, rating);
CREATE INDEX idx_reviews_user_created ON reviews(user_id, created_at);

-- Индексы для таблицы orders
CREATE INDEX idx_orders_user_status ON orders(user_id, status);
CREATE INDEX idx_orders_created_at ON orders(created_at);

-- Индексы для таблицы orders_items
CREATE INDEX idx_orders_items_order_product ON orders_items(order_id, product_id);

-- Индексы для таблицы event_log
CREATE INDEX idx_event_log_created_type ON event_log(created_at, event_type);