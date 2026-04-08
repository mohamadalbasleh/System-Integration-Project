from flask import Flask, jsonify
from flask_bcrypt import Bcrypt
from flask_cors import CORS
from flask_jwt_extended import JWTManager

from config import Config
from models import db

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)
bcrypt = Bcrypt(app)
jwt = JWTManager(app)
CORS(app)


@app.route("/", methods=["GET"])
def home():
    return jsonify({"message": "Online Bookstore API is running"}), 200


from routes_users import *
from routes_books import *
from routes_cart_orders import *

if __name__ == "__main__":
    app.run(debug=True)