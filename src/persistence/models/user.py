from datetime import datetime, timezone
import bcrypt
from src.server.extensions import db


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False, default="player")  # "gm" | "player"
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    characters = db.relationship(
        "Character", backref="owner", lazy=True, cascade="all, delete-orphan",
        foreign_keys="Character.user_id",
    )
    campaigns = db.relationship(
        "Campaign", backref="gm", lazy=True, foreign_keys="Campaign.gm_id"
    )

    def set_password(self, password: str) -> None:
        self.password_hash = bcrypt.hashpw(
            password.encode("utf-8"), bcrypt.gensalt()
        ).decode("utf-8")

    def check_password(self, password: str) -> bool:
        return bcrypt.checkpw(
            password.encode("utf-8"), self.password_hash.encode("utf-8")
        )

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "username": self.username,
            "role": self.role,
            "created_at": self.created_at.isoformat(),
        }
