from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from src.server.extensions import db
from src.models.character import Character
from src.models.user import User

characters_bp = Blueprint("characters", __name__)


def _current_user() -> User | None:
    uid = int(get_jwt_identity())
    return db.session.get(User, uid)


@characters_bp.route("/", methods=["GET"])
@jwt_required()
def list_characters():
    user = _current_user()
    if not user:
        return jsonify({"error": "User not found"}), 404
    # GM sees all, player sees only their own
    if user.role == "gm":
        chars = Character.query.all()
    else:
        chars = Character.query.filter_by(user_id=user.id).all()
    return jsonify([c.to_dict() for c in chars]), 200


@characters_bp.route("/", methods=["POST"])
@jwt_required()
def create_character():
    user = _current_user()
    if not user:
        return jsonify({"error": "User not found"}), 404

    body = request.get_json()
    if not body or not body.get("name"):
        return jsonify({"error": "Character name required"}), 400

    char = Character(
        name=body["name"],
        user_id=user.id,
        campaign_id=body.get("campaign_id"),
    )
    char.data = body.get("data", {})
    db.session.add(char)
    db.session.commit()
    return jsonify(char.to_dict()), 201


@characters_bp.route("/<int:char_id>", methods=["GET"])
@jwt_required()
def get_character(char_id: int):
    user = _current_user()
    char = db.session.get(Character, char_id)
    if not char:
        return jsonify({"error": "Not found"}), 404
    if user.role != "gm" and char.user_id != user.id:
        return jsonify({"error": "Forbidden"}), 403
    return jsonify(char.to_dict()), 200


@characters_bp.route("/<int:char_id>", methods=["PUT"])
@jwt_required()
def update_character(char_id: int):
    user = _current_user()
    char = db.session.get(Character, char_id)
    if not char:
        return jsonify({"error": "Not found"}), 404
    if user.role != "gm" and char.user_id != user.id:
        return jsonify({"error": "Forbidden"}), 403

    body = request.get_json() or {}
    if "name" in body:
        char.name = body["name"]
    if "data" in body:
        char.data = body["data"]
    if "campaign_id" in body:
        char.campaign_id = body["campaign_id"]

    db.session.commit()
    return jsonify(char.to_dict()), 200


@characters_bp.route("/<int:char_id>", methods=["DELETE"])
@jwt_required()
def delete_character(char_id: int):
    user = _current_user()
    char = db.session.get(Character, char_id)
    if not char:
        return jsonify({"error": "Not found"}), 404
    if user.role != "gm" and char.user_id != user.id:
        return jsonify({"error": "Forbidden"}), 403

    db.session.delete(char)
    db.session.commit()
    return jsonify({"message": "Deleted"}), 200
