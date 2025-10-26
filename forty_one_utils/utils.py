import re
import uuid
from datetime import datetime, UTC, timedelta

import jwt

import config
from forty_one_utils.database import FORefreshToken


def validate_username(username):  # works
    if not 8 <= len(username) <= 20:
        return {"is_valid": False, "details": "Username should be 8 to 20 characters"}
    if not re.match(config.ALNUM_PATTERN, username):
        return {"is_valid": False, "details": "Username should only contain alphanumeric characters"}

    return {"is_valid": True, "details": ""}


def validate_email(email):  # works
    if not 15 <= len(email) <= 100:
        return {"is_valid": False, "details": "Email should be 15 to 100 characters"}
    if not re.match(config.EMAIL_PATTERN, email):
        return {"is_valid": False, "details": "Invalid email"}

    return {"is_valid": True, "details": ""}


def validate_password(password):  # works
    if not 8 <= len(password) <= 20:
        return {"is_valid": False, "details": "Password should be 8 to 20 characters"}
    if not re.match(config.ALNUM_PATTERN, password):
        return {"is_valid": False, "details": "Password should only contain alphanumeric characters"}

    return {"is_valid": True, "details": ""}

def create_refresh_token(player_id):
    token = str(uuid.uuid4())
    expires_at = (datetime.now(UTC) + timedelta(days=30)).isoformat()  # 30 days lifetime

    FORefreshToken.query.filter_by(player_id=player_id).delete()

    refresh_token = FORefreshToken(
        token=token,
        player_id=player_id,
        expires_at=expires_at
    )

    config.db.session.add(refresh_token)
    config.db.session.commit()

    return token

def create_access_token(player_id):
    return jwt.encode({
        "player_id": player_id,
        "exp": datetime.now(UTC) + timedelta(minutes=60)
    }, config.api.config['SECRET_KEY'], algorithm='HS256')