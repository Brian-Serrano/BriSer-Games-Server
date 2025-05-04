import re

import config
from critter_combat_utils.database import Player


def level_to_response(level):
    return {
        "level_id": level.level_id,
        "level_name": level.level_name,
        "level_description": level.level_description,
        "creator_id": level.player.player_id,
        "creator_name": level.player.player_name,
        "version": level.version,
        "difficulty": level.difficulty,
        "downloads": level.downloads,
        "likes": level.likes,
        "is_rated": level.is_rated,
        "num_of_coins": level.coins,
        "num_of_diamonds": level.diamonds
    }


def comment_to_response(comment):
    return {
        "comment_id": comment.comment_id,
        "comment_description": comment.comment_description,
        "likes": comment.likes,
        "player_name": Player.query.filter_by(player_id=comment.player_id).first().player_name,
        "player_id": comment.player_id
    }


def increase_version(version):
    return str(round(float(version) + 0.1, 1))


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


def is_number(string):
    return re.match(config.DIGIT_PATTERN, string) is not None


def check_for_bad_word(string):
    return False
