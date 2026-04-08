from flask import request, jsonify
from flask_jwt_extended import create_access_token
from sqlalchemy import func

from app import app, bcrypt
from models import db, User, Cart


@app.route("/api/users/register", methods=["POST"])
def register():
    data = request.get_json()

    if not data:
        return jsonify({"message": "Request body is required"}), 400

    name = data.get("name")
    email = data.get("email")
    password = data.get("password")

    if not name or not email or not password:
        return jsonify({"message": "Name, email, and password are required"}), 400

    existing_user = User.query.filter(func.lower(User.email) == email.lower()).first()
    if existing_user:
        return jsonify({"message": "Email already exists"}), 400

    hashed_password = bcrypt.generate_password_hash(password).decode("utf-8")

    new_user = User(
        name=name,
        email=email.lower(),
        password_hash=hashed_password
    )

    db.session.add(new_user)
    db.session.commit()

    new_cart = Cart(user_id=new_user.user_id)
    db.session.add(new_cart)
    db.session.commit()

    return jsonify({"message": "User registered successfully"}), 201


@app.route("/api/users/login", methods=["POST"])
def login():
    data = request.get_json()

    if not data:
        return jsonify({"message": "Request body is required"}), 400

    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({"message": "Email and password are required"}), 400

    user = User.query.filter(func.lower(User.email) == email.lower()).first()

    if not user or not bcrypt.check_password_hash(user.password_hash, password):
        return jsonify({"message": "Invalid email or password"}), 401

    token = create_access_token(identity=str(user.user_id))

    return jsonify({
        "message": "Login successful",
        "token": token,
        "user": {
            "user_id": user.user_id,
            "name": user.name,
            "email": user.email
        }
    }), 200