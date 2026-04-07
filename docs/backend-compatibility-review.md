# Backend Compatibility Review

This review compares the zipped backend (`online-bookstore-backend.zip`) with:

- the approved ER diagram
- the Phase 1 frontend in [`bookstore/api.js`](/c:/Users/cryox/OneDrive/Documents/GitHub/System-Integration-Project/bookstore/api.js)
- the screens in the supplied presentation

## Verdict

The zipped backend is not correct as submitted. It needs schema changes, endpoint additions, and response-shape changes before it is compatible with the frontend and the approved ER diagram.

## Required fixes

1. The ER diagram includes a separate `Cart` entity, but the backend stores `user_id` directly on `cart_items`. This breaks the `Users -> Cart -> CartItems` relationship required by the design.
2. The ER diagram requires `Users.created_at`, `Orders.created_at`, and `Orders.status`, but the backend models omit those fields.
3. The checkout screen sends `shipping_address` to `POST /api/orders`, but the backend does not store that field.
4. The frontend calls `PUT /api/cart/items/:id` to change quantity. The backend only implements `POST` and `DELETE` for cart items, so quantity updates currently fail.
5. The frontend calls `GET /api/orders` to display order history. The backend only implements `POST /api/orders`, so the orders page cannot load.
6. The frontend registration form sends `name`, but the backend expects `full_name`. `POST /api/users/register` will reject the current UI payload.
7. The login and register pages expect a JWT plus a user object or user name for local storage. The backend returns only a token on login and only a message on registration.
8. The frontend catalog page expects filtering, search, sorting, and pagination parameters on `GET /api/books`. The backend returns all books without query support.
9. The frontend cart page expects each cart item to contain price data and book details. The backend returns only `cart_item_id`, `book_id`, `title`, and `quantity`.
10. The frontend order page expects nested order items, totals, status, and date information. The backend returns only the result of order creation.
11. The backend uses `db.Float` for prices and totals. PostgreSQL `NUMERIC(10,2)` should be used for money fields to avoid rounding issues.
12. The PostgreSQL connection string is hard-coded in source with credentials. It should be moved to environment variables before submission.

## Correct target contract

The database should use the ER diagram entities:

- `users`
- `categories`
- `books`
- `cart`
- `cart_items`
- `orders`
- `order_items`

The API should implement:

- `POST /api/users/register`
- `POST /api/users/login`
- `GET /api/categories`
- `GET /api/books`
- `GET /api/books/{book_id}`
- `GET /api/cart`
- `POST /api/cart/items`
- `PUT /api/cart/items/{cart_item_id}`
- `DELETE /api/cart/items/{cart_item_id}`
- `GET /api/orders`
- `POST /api/orders`

## Recommendation

Use [`database/schema.sql`](/c:/Users/cryox/OneDrive/Documents/GitHub/System-Integration-Project/database/schema.sql) as the database source of truth and [`postman/online-bookstore.postman_collection.json`](/c:/Users/cryox/OneDrive/Documents/GitHub/System-Integration-Project/postman/online-bookstore.postman_collection.json) as the API contract for testing and documentation.
