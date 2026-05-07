from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from src.server.extensions import db
from src.persistence.models.user import User

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400

    username = data.get("username", "").strip()
    password = data.get("password", "")
    role = data.get("role", "player")

    if not username or not password:
        return jsonify({"error": "Username and password required"}), 400
    if not (3 <= len(username) <= 50):
        return jsonify({"error": "Username must be 3–50 characters"}), 400
    if len(password) < 6:
        return jsonify({"error": "Password must be at least 6 characters"}), 400
    if role not in ("gm", "player"):
        return jsonify({"error": "Invalid role"}), 400
    if role == "gm" and User.query.filter_by(role="gm").first():
        return jsonify({"error": "A GM account already exists on this server"}), 409
    if User.query.filter_by(username=username).first():
        return jsonify({"error": "Username already taken"}), 409

    user = User(username=username, role=role)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()

    token = create_access_token(identity=str(user.id))
    return jsonify({"token": token, "user": user.to_dict()}), 201


@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400

    username = data.get("username", "").strip()
    password = data.get("password", "")

    user = User.query.filter_by(username=username).first()
    if not user or not user.check_password(password):
        return jsonify({"error": "Invalid credentials"}), 401

    token = create_access_token(identity=str(user.id))
    return jsonify({"token": token, "user": user.to_dict()}), 200


@auth_bp.route("/me", methods=["GET"])
@jwt_required()
def me():
    user_id = int(get_jwt_identity())
    user = db.session.get(User, user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404
    return jsonify(user.to_dict()), 200


@auth_bp.route("/has-gm", methods=["GET"])
def has_gm():
    exists = User.query.filter_by(role="gm").first() is not None
    return jsonify({"has_gm": exists}), 200
