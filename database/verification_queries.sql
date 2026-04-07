-- Registration test
SELECT user_id, name, email, created_at
FROM users
WHERE email = 'amira.reader@example.com';

-- Catalog/category test
SELECT b.book_id, b.title, c.name AS category, b.price
FROM books b
JOIN categories c ON c.category_id = b.category_id
ORDER BY b.book_id;

-- Cart before/after add or update test
SELECT
    c.cart_id,
    u.email,
    ci.cart_item_id,
    b.title,
    ci.quantity,
    b.price
FROM cart c
JOIN users u ON u.user_id = c.user_id
LEFT JOIN cart_items ci ON ci.cart_id = c.cart_id
LEFT JOIN books b ON b.book_id = ci.book_id
WHERE u.email = 'demo@pageturn.com'
ORDER BY ci.cart_item_id;

-- Orders before/after checkout test
SELECT
    o.order_id,
    u.email,
    o.total_price,
    o.status,
    o.shipping_address,
    o.created_at
FROM orders o
JOIN users u ON u.user_id = o.user_id
WHERE u.email = 'demo@pageturn.com'
ORDER BY o.order_id DESC;

SELECT
    oi.order_item_id,
    oi.order_id,
    b.title,
    oi.quantity,
    oi.price
FROM order_items oi
JOIN books b ON b.book_id = oi.book_id
ORDER BY oi.order_item_id DESC;
