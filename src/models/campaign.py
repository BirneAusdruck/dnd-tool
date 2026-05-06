import json
import secrets
from datetime import datetime, timezone
from src.server.extensions import db


class Campaign(db.Model):
    __tablename__ = "campaigns"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    gm_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    join_code = db.Column(db.String(8), unique=True, nullable=False)
    is_active = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    _content = db.Column(db.Text, default="{}")

    characters = db.relationship(
        "Character", backref="campaign", lazy=True, foreign_keys="Character.campaign_id"
    )

    def __init__(self, **kwargs):
        if "join_code" not in kwargs:
            kwargs["join_code"] = secrets.token_hex(4).upper()
        super().__init__(**kwargs)

    @property
    def content(self) -> dict:
        try:
            return json.loads(self._content or "{}")
        except (json.JSONDecodeError, TypeError):
            return {}

    @content.setter
    def content(self, value: dict) -> None:
        self._content = json.dumps(value, ensure_ascii=False)

    def to_dict(self, include_content: bool = False) -> dict:
        d = {
            "id": self.id,
            "name": self.name,
            "gm_id": self.gm_id,
            "join_code": self.join_code,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
        c = self.content
        d["chapter_count"]   = len(c.get("chapters", []))
        d["npc_count"]       = len(c.get("npcs", []))
        d["item_count"]      = len(c.get("items", []))
        d["encounter_count"] = len(c.get("encounters", []))
        if include_content:
            d["content"] = c
        return d
