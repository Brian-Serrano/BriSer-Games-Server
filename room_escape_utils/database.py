from datetime import datetime, UTC

from config import db


class Player(db.Model):
    __tablename__ = "room_escape_player"

    player_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    player_name = db.Column(db.String(20), nullable=False, default="Player")
    email = db.Column(db.String(100), nullable=False, default="player@nothing.com")
    password = db.Column(db.String(128), nullable=False, default="player123")
    total_coins = db.Column(db.Integer, nullable=False, default=0)
    level = db.Column(db.Integer, nullable=False, default=0)
    high_score = db.Column(db.Integer, nullable=False, default=0)

    # Refresh tokens stored per user (optional: allow multiple sessions)
    refresh_tokens = db.relationship("RERefreshToken", backref="player", lazy=True)


class RERefreshToken(db.Model):
    __tablename__ = "room_escape_refresh_token"

    id = db.Column(db.Integer, primary_key=True)
    token = db.Column(db.String(255), unique=True, nullable=False, index=True)
    expires_at = db.Column(db.String, nullable=False)
    player_id = db.Column(db.Integer, db.ForeignKey("room_escape_player.player_id"), nullable=False)

    def is_expired(self):
        return datetime.now(UTC) > datetime.fromisoformat(self.expires_at)