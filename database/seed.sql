-- Seed data for PageTurn Online Bookstore
-- Run AFTER schema.sql: psql -d bookstore -f database/seed.sql

BEGIN;

-- Categories
INSERT INTO categories (name) VALUES
  ('Fiction'),
  ('Science'),
  ('Technology'),
  ('History'),
  ('Business'),
  ('Art');

-- Books (25 stock each by default)
INSERT INTO books (title, author, description, price, category_id, isbn, rating, pages) VALUES
  -- Fiction (category_id = 1)
  ('The Great Gatsby', 'F. Scott Fitzgerald', 'A novel about the American Dream set in the Jazz Age.', 12.99, 1, '9780743273565', 4.50, 180),
  ('To Kill a Mockingbird', 'Harper Lee', 'A timeless story of racial injustice in the Deep South.', 14.99, 1, '9780061120084', 4.80, 281),
  ('1984', 'George Orwell', 'A dystopian novel about surveillance and totalitarianism.', 11.99, 1, '9780451524935', 4.70, 328),
  ('Pride and Prejudice', 'Jane Austen', 'A romantic novel about manners and love in Regency England.', 9.99, 1, '9780141439518', 4.60, 432),

  -- Science (category_id = 2)
  ('A Brief History of Time', 'Stephen Hawking', 'An exploration of cosmology and the nature of the universe.', 18.99, 2, '9780553380163', 4.50, 256),
  ('Cosmos', 'Carl Sagan', 'A journey through space and human understanding of the universe.', 16.99, 2, '9780345539434', 4.70, 396),
  ('The Selfish Gene', 'Richard Dawkins', 'A groundbreaking work on evolutionary biology and genetics.', 15.49, 2, '9780199291151', 4.30, 360),

  -- Technology (category_id = 3)
  ('Clean Code', 'Robert C. Martin', 'A handbook of agile software craftsmanship.', 39.99, 3, '9780132350884', 4.40, 464),
  ('The Pragmatic Programmer', 'David Thomas & Andrew Hunt', 'Practical advice for modern software developers.', 44.99, 3, '9780135957059', 4.60, 352),
  ('Designing Data-Intensive Applications', 'Martin Kleppmann', 'The big ideas behind reliable, scalable, and maintainable systems.', 42.99, 3, '9781449373320', 4.80, 616),

  -- History (category_id = 4)
  ('Sapiens', 'Yuval Noah Harari', 'A brief history of humankind from the Stone Age to the present.', 19.99, 4, '9780062316097', 4.50, 464),
  ('Guns, Germs, and Steel', 'Jared Diamond', 'Why some civilizations conquered others.', 17.49, 4, '9780393354324', 4.30, 528),
  ('The Silk Roads', 'Peter Frankopan', 'A new history of the world through the lens of trade routes.', 18.99, 4, '9781101912379', 4.20, 636),

  -- Business (category_id = 5)
  ('Zero to One', 'Peter Thiel', 'Notes on startups and how to build the future.', 22.99, 5, '9780804139298', 4.20, 224),
  ('Thinking, Fast and Slow', 'Daniel Kahneman', 'How two systems of thinking shape our judgments and decisions.', 17.99, 5, '9780374533557', 4.50, 499),
  ('The Lean Startup', 'Eric Ries', 'A method for developing businesses and products efficiently.', 24.99, 5, '9780307887894', 4.10, 336),

  -- Art (category_id = 6)
  ('Ways of Seeing', 'John Berger', 'A groundbreaking analysis of how we perceive visual art.', 13.99, 6, '9780140135152', 4.20, 176),
  ('The Story of Art', 'E.H. Gombrich', 'One of the most famous introductions to the history of art.', 29.99, 6, '9780714832470', 4.60, 688),
  ('Steal Like an Artist', 'Austin Kleon', 'Creative advice for the digital age.', 11.99, 6, '9780761169253', 4.10, 160);

COMMIT;
