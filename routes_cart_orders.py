from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from app import app
from models import db, Cart, CartItem, Book, Order, OrderItem, Category


def get_user_cart(user_id):
    return Cart.query.filter_by(user_id=user_id).first()


@app.route("/api/cart", methods=["GET"])
@jwt_required()
def get_cart():
    user_id = int(get_jwt_identity())
    cart = get_user_cart(user_id)

    if not cart:
        return jsonify({"items": [], "total": 0}), 200

    items = CartItem.query.filter_by(cart_id=cart.cart_id).all()

    result_items = []
    total = 0

    for item in items:
        book = Book.query.get(item.book_id)
        if book:
            cat = Category.query.get(book.category_id)
            subtotal = float(book.price) * item.quantity
            total += subtotal

            result_items.append({
                "cart_item_id": item.cart_item_id,
                "id": item.cart_item_id,
                "book_id": book.book_id,
                "title": book.title,
                "author": book.author,
                "price": float(book.price),
                "category": cat.name if cat else "General",
                "quantity": item.quantity,
                "subtotal": subtotal
            })

    return jsonify({
        "items": result_items,
        "total": total
    }), 200


@app.route("/api/cart/items", methods=["POST"])
@jwt_required()
def add_to_cart():
    user_id = int(get_jwt_identity())
    data = request.get_json()

    if not data:
        return jsonify({"message": "Request body is required"}), 400

    book_id = data.get("book_id")
    quantity = data.get("quantity", 1)

    if not book_id:
        return jsonify({"message": "book_id is required"}), 400

    try:
        quantity = int(quantity)
    except (ValueError, TypeError):
        return jsonify({"message": "Quantity must be a number"}), 400

    if quantity < 1:
        return jsonify({"message": "Quantity must be at least 1"}), 400

    book = Book.query.get(book_id)
    if not book:
        return jsonify({"message": "Book not found"}), 404

    if book.stock < quantity:
        return jsonify({"message": "Not enough stock available"}), 400

    cart = get_user_cart(user_id)
    if not cart:
        cart = Cart(user_id=user_id)
        db.session.add(cart)
        db.session.commit()

    existing_item = CartItem.query.filter_by(cart_id=cart.cart_id, book_id=book_id).first()

    if existing_item:
        existing_item.quantity += quantity
    else:
        new_item = CartItem(
            cart_id=cart.cart_id,
            book_id=book_id,
            quantity=quantity
        )
        db.session.add(new_item)

    db.session.commit()

    return jsonify({"message": "Book added to cart"}), 201


@app.route("/api/cart/items/<int:item_id>", methods=["PUT"])
@jwt_required()
def update_cart_item(item_id):
    user_id = int(get_jwt_identity())
    cart = get_user_cart(user_id)

    if not cart:
        return jsonify({"message": "Cart not found"}), 404

    item = CartItem.query.filter_by(cart_item_id=item_id, cart_id=cart.cart_id).first()

    if not item:
        return jsonify({"message": "Cart item not found"}), 404

    data = request.get_json()
    if not data:
        return jsonify({"message": "Request body is required"}), 400

    quantity = data.get("quantity")
    if quantity is None:
        return jsonify({"message": "Quantity is required"}), 400

    try:
        quantity = int(quantity)
    except (ValueError, TypeError):
        return jsonify({"message": "Quantity must be a number"}), 400

    if quantity < 1:
        return jsonify({"message": "Quantity must be at least 1"}), 400

    book = Book.query.get(item.book_id)
    if book and quantity > book.stock:
        return jsonify({"message": "Not enough stock available"}), 400

    item.quantity = quantity
    db.session.commit()

    return jsonify({"message": "Cart item updated"}), 200


@app.route("/api/cart/items/<int:item_id>", methods=["DELETE"])
@jwt_required()
def delete_cart_item(item_id):
    user_id = int(get_jwt_identity())
    cart = get_user_cart(user_id)

    if not cart:
        return jsonify({"message": "Cart not found"}), 404

    item = CartItem.query.filter_by(cart_item_id=item_id, cart_id=cart.cart_id).first()

    if not item:
        return jsonify({"message": "Cart item not found"}), 404

    db.session.delete(item)
    db.session.commit()

    return jsonify({"message": "Item removed from cart"}), 200


@app.route("/api/orders", methods=["POST"])
@jwt_required()
def create_order():
    user_id = int(get_jwt_identity())
    data = request.get_json()

    if not data:
        return jsonify({"message": "Request body is required"}), 400

    shipping_address = (data.get("shipping_address") or "").strip()

    if not shipping_address:
        return jsonify({"message": "Shipping address is required"}), 400

    cart = get_user_cart(user_id)
    if not cart:
        return jsonify({"message": "Cart not found"}), 404

    cart_items = CartItem.query.filter_by(cart_id=cart.cart_id).all()

    if not cart_items:
        return jsonify({"message": "Cart is empty"}), 400

    new_order = Order(
        user_id=user_id,
        shipping_address=shipping_address,
        total_price=0,
        status="pending"
    )
    db.session.add(new_order)
    db.session.commit()

    total_price = 0

    for item in cart_items:
        book = Book.query.get(item.book_id)
        if book:
            line_total = float(book.price) * item.quantity
            total_price += line_total

            order_item = OrderItem(
                order_id=new_order.order_id,
                book_id=book.book_id,
                quantity=item.quantity,
                price=book.price
            )
            db.session.add(order_item)

            book.stock = max(0, book.stock - item.quantity)

    new_order.total_price = total_price

    for item in cart_items:
        db.session.delete(item)

    db.session.commit()

    return jsonify({
        "message": "Order created successfully",
        "order_id": new_order.order_id,
        "id": new_order.order_id,
        "total_price": total_price
    }), 201


@app.route("/api/orders", methods=["GET"])
@jwt_required()
def get_orders():
    user_id = int(get_jwt_identity())

    orders = Order.query.filter_by(user_id=user_id).order_by(Order.order_id.desc()).all()

    result = []
    for order in orders:
        order_items = OrderItem.query.filter_by(order_id=order.order_id).all()
        items = []
        for oi in order_items:
            book = Book.query.get(oi.book_id)
            cat = Category.query.get(book.category_id) if book else None
            items.append({
                "order_item_id": oi.order_item_id,
                "book_id": oi.book_id,
                "title": book.title if book else "Unknown",
                "author": book.author if book else "",
                "category": cat.name if cat else "General",
                "quantity": oi.quantity,
                "price": float(oi.price)
            })

        result.append({
            "order_id": order.order_id,
            "id": order.order_id,
            "total_price": float(order.total_price),
            "total": float(order.total_price),
            "status": order.status,
            "shipping_address": order.shipping_address,
            "created_at": order.created_at.isoformat() if order.created_at else None,
            "items": items
        })

    return jsonify(result), 200