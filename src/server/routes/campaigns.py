"""
Campaign CRUD endpoints.

GET    /api/campaigns/        list (GM sees all, player sees joined)
POST   /api/campaigns/        create new campaign (GM only)
GET    /api/campaigns/<id>    full campaign + content
PUT    /api/campaigns/<id>    update name / content (GM only)
DELETE /api/campaigns/<id>    delete (GM only)
"""
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt, get_jwt_identity

from src.server.extensions import db
from src.models.campaign import Campaign

campaigns_bp = Blueprint("campaigns", __name__)


def _require_gm():
    claims = get_jwt()
    if claims.get("role") != "gm":
        return jsonify({"error": "Nur der GM darf Kampagnen verwalten."}), 403
    return None


@campaigns_bp.route("/", methods=["GET"])
@jwt_required()
def list_campaigns():
    campaigns = Campaign.query.order_by(Campaign.created_at.desc()).all()
    return jsonify([c.to_dict() for c in campaigns]), 200


@campaigns_bp.route("/", methods=["POST"])
@jwt_required()
def create_campaign():
    err = _require_gm()
    if err:
        return err
    data = request.get_json(force=True) or {}
    name = (data.get("name") or "").strip()
    if not name:
        return jsonify({"error": "Name darf nicht leer sein."}), 400

    user_id = int(get_jwt_identity())
    campaign = Campaign(name=name, gm_id=user_id)
    campaign.content = {
        "chapters":   [],
        "npcs":       [],
        "items":      [],
        "encounters": [],
        "flags":      [],
    }
    db.session.add(campaign)
    db.session.commit()
    return jsonify(campaign.to_dict(include_content=True)), 201


@campaigns_bp.route("/<int:campaign_id>", methods=["GET"])
@jwt_required()
def get_campaign(campaign_id: int):
    c = db.session.get(Campaign, campaign_id)
    if not c:
        return jsonify({"error": "Kampagne nicht gefunden."}), 404
    return jsonify(c.to_dict(include_content=True)), 200


@campaigns_bp.route("/<int:campaign_id>", methods=["PUT"])
@jwt_required()
def update_campaign(campaign_id: int):
    err = _require_gm()
    if err:
        return err
    c = db.session.get(Campaign, campaign_id)
    if not c:
        return jsonify({"error": "Kampagne nicht gefunden."}), 404

    data = request.get_json(force=True) or {}
    if "name" in data:
        c.name = data["name"].strip() or c.name
    if "content" in data:
        c.content = data["content"]
    if "is_active" in data:
        c.is_active = bool(data["is_active"])
    db.session.commit()
    return jsonify(c.to_dict(include_content=True)), 200


@campaigns_bp.route("/<int:campaign_id>", methods=["DELETE"])
@jwt_required()
def delete_campaign(campaign_id: int):
    err = _require_gm()
    if err:
        return err
    c = db.session.get(Campaign, campaign_id)
    if not c:
        return jsonify({"error": "Kampagne nicht gefunden."}), 404
    db.session.delete(c)
    db.session.commit()
    return jsonify({"ok": True}), 200
