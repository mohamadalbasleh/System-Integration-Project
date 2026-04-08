from flask import jsonify, request
from sqlalchemy import or_

from app import app
from models import Category, Book


@app.route("/api/categories", methods=["GET"])
def get_categories():
    categories = Category.query.order_by(Category.name).all()

    result = []
    for category in categories:
        result.append({
            "category_id": category.category_id,
            "name": category.name
        })

    return jsonify(result), 200


@app.route("/api/books", methods=["GET"])
def get_books():
    search = request.args.get("search", "").strip()

    query = Book.query
    if search:
        query = query.filter(
            or_(
                Book.title.ilike(f"%{search}%"),
                Book.author.ilike(f"%{search}%")
            )
        )

    books = query.order_by(Book.book_id).all()

    result = []
    for book in books:
        result.append({
            "book_id": book.book_id,
            "title": book.title,
            "author": book.author,
            "description": book.description,
            "price": float(book.price),
            "category_id": book.category_id,
            "cover_url": book.cover_url,
            "isbn": book.isbn,
            "rating": float(book.rating) if book.rating is not None else None,
            "pages": book.pages,
            "stock": book.stock
        })

    return jsonify(result), 200


@app.route("/api/books/<int:book_id>", methods=["GET"])
def get_book(book_id):
    book = Book.query.get(book_id)

    if not book:
        return jsonify({"message": "Book not found"}), 404

    return jsonify({
        "book_id": book.book_id,
        "title": book.title,
        "author": book.author,
        "description": book.description,
        "price": float(book.price),
        "category_id": book.category_id,
        "cover_url": book.cover_url,
        "isbn": book.isbn,
        "rating": float(book.rating) if book.rating is not None else None,
        "pages": book.pages,
        "stock": book.stock
    }), 200