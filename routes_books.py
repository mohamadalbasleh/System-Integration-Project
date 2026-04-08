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
    category = request.args.get("category", "").strip()
    sort = request.args.get("sort", "").strip()
    page = request.args.get("page", 1, type=int)
    limit = request.args.get("limit", 12, type=int)

    if page < 1:
        page = 1
    if limit < 1 or limit > 100:
        limit = 12

    query = Book.query.join(Category, Book.category_id == Category.category_id)

    if search:
        query = query.filter(
            or_(
                Book.title.ilike(f"%{search}%"),
                Book.author.ilike(f"%{search}%")
            )
        )

    if category:
        query = query.filter(Category.name.ilike(category))

    if sort == "price_asc":
        query = query.order_by(Book.price.asc())
    elif sort == "price_desc":
        query = query.order_by(Book.price.desc())
    elif sort == "title":
        query = query.order_by(Book.title.asc())
    elif sort == "rating":
        query = query.order_by(Book.rating.desc().nullslast())
    else:
        query = query.order_by(Book.book_id)

    total = query.count()
    books = query.offset((page - 1) * limit).limit(limit).all()

    result = []
    for book in books:
        cat = Category.query.get(book.category_id)
        result.append({
            "id": book.book_id,
            "book_id": book.book_id,
            "title": book.title,
            "author": book.author,
            "description": book.description,
            "price": float(book.price),
            "category_id": book.category_id,
            "category": cat.name if cat else "General",
            "cover_url": book.cover_url,
            "isbn": book.isbn,
            "rating": float(book.rating) if book.rating is not None else None,
            "pages": book.pages,
            "stock": book.stock
        })

    return jsonify({"books": result, "total": total, "page": page, "limit": limit}), 200


@app.route("/api/books/<int:book_id>", methods=["GET"])
def get_book(book_id):
    book = Book.query.get(book_id)

    if not book:
        return jsonify({"message": "Book not found"}), 404

    cat = Category.query.get(book.category_id)

    return jsonify({
        "id": book.book_id,
        "book_id": book.book_id,
        "title": book.title,
        "author": book.author,
        "description": book.description,
        "price": float(book.price),
        "category_id": book.category_id,
        "category": cat.name if cat else "General",
        "cover_url": book.cover_url,
        "isbn": book.isbn,
        "rating": float(book.rating) if book.rating is not None else None,
        "pages": book.pages,
        "stock": book.stock
    }), 200