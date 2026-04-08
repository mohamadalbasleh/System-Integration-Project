from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from app import app
from models import db, Cart, CartItem, Book, Order, OrderItem


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
            subtotal = float(book.price) * item.quantity
            total += subtotal

            result_items.append({
                "cart_item_id": item.cart_item_id,
                "book_id": book.book_id,
                "title": book.title,
                "author": book.author,
                "price": float(book.price),
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
    except ValueError:
        return jsonify({"message": "Quantity must be a number"}), 400

    if quantity < 1:
        return jsonify({"message": "Quantity must be at least 1"}), 400

    book = Book.query.get(book_id)
    if not book:
        return jsonify({"message": "Book not found"}), 404

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

    shipping_address = data.get("shipping_address")

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

    new_order.total_price = total_price

    for item in cart_items:
        db.session.delete(item)

    db.session.commit()

    return jsonify({
        "message": "Order created successfully",
        "order_id": new_order.order_id,
        "total_price": total_price
    }), 201


@app.route("/api/orders", methods=["GET"])
@jwt_required()
def get_orders():
    user_id = int(get_jwt_identity())

    orders = Order.query.filter_by(user_id=user_id).order_by(Order.order_id.desc()).all()

    result = []
    for order in orders:
        result.append({
            "order_id": order.order_id,
            "total_price": float(order.total_price),
            "status": order.status,
            "shipping_address": order.shipping_address,
            "created_at": order.created_at.isoformat() if order.created_at else None
        })

    return jsonify(result), 200