BEGIN;

INSERT INTO categories (name)
VALUES
    ('Fiction'),
    ('Technology'),
    ('Science'),
    ('Business')
ON CONFLICT (name) DO NOTHING;

INSERT INTO books (title, author, description, price, category_id, isbn, rating, pages, stock)
SELECT *
FROM (
    VALUES
        ('The Great Gatsby', 'F. Scott Fitzgerald', 'A classic novel about wealth, longing, and the American dream.', 15.00, (SELECT category_id FROM categories WHERE name = 'Fiction'), '9780743273565', 4.70, 180, 18),
        ('Clean Code', 'Robert C. Martin', 'A practical guide to writing maintainable and readable software.', 29.99, (SELECT category_id FROM categories WHERE name = 'Technology'), '9780132350884', 4.80, 464, 12),
        ('A Brief History of Time', 'Stephen Hawking', 'An accessible introduction to cosmology and modern physics.', 19.99, (SELECT category_id FROM categories WHERE name = 'Science'), '9780553380163', 4.60, 256, 10),
        ('The Lean Startup', 'Eric Ries', 'A framework for building products with validated learning.', 24.99, (SELECT category_id FROM categories WHERE name = 'Business'), '9780307887894', 4.50, 336, 15)
) AS seed_books(title, author, description, price, category_id, isbn, rating, pages, stock)
WHERE NOT EXISTS (
    SELECT 1
    FROM books b
    WHERE b.title = seed_books.title
      AND b.author = seed_books.author
);

INSERT INTO users (name, email, password_hash)
SELECT
    'Demo Reader',
    'demo@pageturn.com',
    crypt('Password123!', gen_salt('bf'))
WHERE NOT EXISTS (
    SELECT 1
    FROM users
    WHERE email = 'demo@pageturn.com'
);

INSERT INTO cart (user_id)
SELECT user_id
FROM users
WHERE email = 'demo@pageturn.com'
  AND NOT EXISTS (
      SELECT 1
      FROM cart c
      WHERE c.user_id = users.user_id
  );

COMMIT;
