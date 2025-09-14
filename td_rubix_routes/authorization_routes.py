import bcrypt
from flask import Blueprint, request, jsonify

from td_rubix_utils.database import Player, TRRefreshToken
from td_rubix_utils.utils import validate_username, validate_email, validate_password, create_access_token, \
    create_refresh_token
from config import db, limiter

authorization_routes = Blueprint("tr_authorization_routes", __name__)


@authorization_routes.route("/sign_up", methods=["POST"])
@limiter.limit("5 per hour")
def sign_up():
    data = request.json

    name_validation = validate_username(data["player_name"])
    email_validation = validate_email(data["email"])
    password_validation = validate_password(data["password"])

    if not name_validation["is_valid"]:
        return jsonify({"error": "Invalid Player name", "details": name_validation["details"]}), 400
    if not email_validation["is_valid"]:
        return jsonify({"error": "Invalid Email", "details": email_validation["details"]}), 400
    if not password_validation["is_valid"]:
        return jsonify({"error": "Invalid Password", "details": password_validation["details"]}), 400
    if data["password"] != data["confirm_password"]:
        return jsonify({"error": "Passwords not match", "details": "Passwords do not match"}), 400
    if db.session.query(Player.player_id).filter_by(player_name=data["player_name"]).first():
        return jsonify({"error": "Player exists.", "details": "Player name already exists"}), 400
    if db.session.query(Player.player_id).filter_by(email=data["email"]).first():
        return jsonify({"error": "Player exists.", "details": "Email already exists"}), 400

    player = Player(
        player_name=data["player_name"],
        email=data["email"],
        password=bcrypt.hashpw(data["password"].encode(), bcrypt.gensalt()).decode()
    )

    db.session.add(player)
    db.session.commit()

    access_token = create_access_token(player.player_id)
    refresh_token = create_refresh_token(player.player_id)

    return jsonify({
        "access_token": access_token,
        "refresh_token": refresh_token,
        "player_id": player.player_id
    }), 201


@authorization_routes.route("/log_in", methods=["POST"])
@limiter.limit("5 per hour")
def log_in():
    data = request.json

    player = Player.query.filter_by(player_name=data["player_name"]).first()

    name_validation = validate_username(data["player_name"])
    password_validation = validate_password(data["password"])

    if not name_validation["is_valid"]:
        return jsonify({"error": "Invalid Player name", "details": name_validation["details"]}), 400
    if not password_validation["is_valid"]:
        return jsonify({"error": "Invalid Password", "details": password_validation["details"]}), 400
    if not player:
        return jsonify({"error": "Not found", "details": "Player not found"}), 400
    if not bcrypt.checkpw(data["password"].encode(), player.password.encode()):
        return jsonify({"error": "Wrong password", "details": "Wrong password"}), 400

    access_token = create_access_token(player.player_id)
    refresh_token = create_refresh_token(player.player_id)

    return jsonify({
        "access_token": access_token,
        "refresh_token": refresh_token,
        "player_id": player.player_id
    }), 201


@authorization_routes.route("/refresh", methods=["POST"])
@limiter.limit("10 per minute")
def refresh():
    data = request.json
    token = data["refresh_token"]

    if not token:
        return jsonify({"error": "Missing token", "details": "Missing refresh token. Please login."}), 400

    stored_token = TRRefreshToken.query.filter_by(token=token).first()
    if not stored_token:
        return jsonify({"error": "Invalid token", "details": "Invalid refresh token. Please login."}), 401

    if stored_token.is_expired():
        db.session.delete(stored_token)
        db.session.commit()
        return jsonify({"error": "Expired token", "details": "Refresh token expired. Please login."}), 401

    player = Player.query.filter_by(player_id=stored_token.player_id).first()

    access_token = create_access_token(player.player_id)
    refresh_token = create_refresh_token(player.player_id)

    return jsonify({"access_token": access_token, "refresh_token": refresh_token}), 201