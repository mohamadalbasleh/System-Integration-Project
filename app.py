import os
from datetime import timedelta

from flask import Flask, jsonify, send_from_directory
from flask_bcrypt import Bcrypt
from flask_cors import CORS
from flask_jwt_extended import JWTManager

from config import Config
from models import db

app = Flask(__name__, static_folder="bookstore", static_url_path="")
app.config.from_object(Config)
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=24)

db.init_app(app)
bcrypt = Bcrypt(app)
jwt = JWTManager(app)
CORS(app)


@app.route("/", methods=["GET"])
def serve_index():
    return send_from_directory(app.static_folder, "index.html")


@app.route("/api", methods=["GET"])
def api_home():
    return jsonify({"message": "Online Bookstore API is running"}), 200


from routes_users import *
from routes_books import *
from routes_cart_orders import *

if __name__ == "__main__":
    app.run(debug=True)