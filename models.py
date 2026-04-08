from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func

db = SQLAlchemy()


class User(db.Model):
    __tablename__ = "users"

    user_id = db.Column(db.BigInteger, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now(), nullable=False)


class Category(db.Model):
    __tablename__ = "categories"

    category_id = db.Column(db.BigInteger, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)


class Book(db.Model):
    __tablename__ = "books"

    book_id = db.Column(db.BigInteger, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    author = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    category_id = db.Column(db.BigInteger, db.ForeignKey("categories.category_id"), nullable=False)
    cover_url = db.Column(db.Text)
    isbn = db.Column(db.String(20))
    rating = db.Column(db.Numeric(3, 2))
    pages = db.Column(db.Integer)
    stock = db.Column(db.Integer, nullable=False, default=25)
    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now(), nullable=False)


class Cart(db.Model):
    __tablename__ = "cart"

    cart_id = db.Column(db.BigInteger, primary_key=True)
    user_id = db.Column(db.BigInteger, db.ForeignKey("users.user_id"), nullable=False, unique=True)
    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now(), nullable=False)


class CartItem(db.Model):
    __tablename__ = "cart_items"

    cart_item_id = db.Column(db.BigInteger, primary_key=True)
    cart_id = db.Column(db.BigInteger, db.ForeignKey("cart.cart_id"), nullable=False)
    book_id = db.Column(db.BigInteger, db.ForeignKey("books.book_id"), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    added_at = db.Column(db.DateTime(timezone=True), server_default=func.now(), nullable=False)


class Order(db.Model):
    __tablename__ = "orders"

    order_id = db.Column(db.BigInteger, primary_key=True)
    user_id = db.Column(db.BigInteger, db.ForeignKey("users.user_id"), nullable=False)
    total_price = db.Column(db.Numeric(10, 2), nullable=False, default=0)
    status = db.Column(db.String(20), nullable=False, default="pending")
    shipping_address = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now(), nullable=False)


class OrderItem(db.Model):
    __tablename__ = "order_items"

    order_item_id = db.Column(db.BigInteger, primary_key=True)
    order_id = db.Column(db.BigInteger, db.ForeignKey("orders.order_id"), nullable=False)
    book_id = db.Column(db.BigInteger, db.ForeignKey("books.book_id"), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Numeric(10, 2), nullable=False)