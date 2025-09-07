from datetime import datetime, timedelta

import bcrypt
import jwt
from flask import Blueprint, request, jsonify

from config import db, api, limiter
from critter_combat_utils.database import Player
from critter_combat_utils.utils import validate_username, validate_email, validate_password

authorization_routes = Blueprint("cc_authorization_routes", __name__)


@authorization_routes.route("/sign_up", methods=["POST"])
@limiter.limit("5 per hour")
def sign_up():
    data = request.json

    name_validation = validate_username(data["player_name"])
    email_validation = validate_email(data["email"])
    password_validation = validate_password(data["password"])

    if not name_validation["is_valid"]:  # works
        return jsonify({"error": "Invalid Player name", "details": name_validation["details"]}), 400
    if not email_validation["is_valid"]:  # works
        return jsonify({"error": "Invalid Email", "details": email_validation["details"]}), 400
    if not password_validation["is_valid"]:  # works
        return jsonify({"error": "Invalid Password", "details": password_validation["details"]}), 400
    if data["password"] != data["confirm_password"]:  # works
        return jsonify({"error": "Passwords not match", "details": "Passwords do not match"}), 400
    if db.session.query(Player.player_id).filter_by(player_name=data["player_name"]).first():  # works
        return jsonify({"error": "Player exists.", "details": "Player name already exists"}), 400
    if db.session.query(Player.player_id).filter_by(email=data["email"]).first():  # works
        return jsonify({"error": "Player exists.", "details": "Email already exists"}), 400

    player = Player(
        player_name=data["player_name"],
        email=data["email"],
        password=bcrypt.hashpw(data["password"].encode(), bcrypt.gensalt()).decode()
    )

    db.session.add(player)
    db.session.commit()

    token = jwt.encode({"player_id": player.player_id, "exp": datetime.now() + timedelta(weeks=5)}, api.config['SECRET_KEY'], algorithm='HS256')

    return jsonify({"token": token, "player_id": player.player_id}), 201


@authorization_routes.route("/log_in", methods=["POST"])
@limiter.limit("5 per hour")
def log_in():
    data = request.json

    player = Player.query.filter_by(player_name=data["player_name"]).first()

    name_validation = validate_username(data["player_name"])
    password_validation = validate_password(data["password"])

    if not name_validation["is_valid"]:  # works
        return jsonify({"error": "Invalid Player name", "details": name_validation["details"]}), 400
    if not password_validation["is_valid"]:  # works
        return jsonify({"error": "Invalid Password", "details": password_validation["details"]}), 400
    if not player:  # works
        return jsonify({"error": "Not found", "details": "Player not found"}), 400
    if not bcrypt.checkpw(data["password"].encode(), player.password.encode()):  # works
        return jsonify({"error": "Wrong password", "details": "Wrong password"}), 400

    token = jwt.encode({"player_id": player.player_id, "exp": datetime.now() + timedelta(weeks=5)}, api.config['SECRET_KEY'], algorithm='HS256')

    return jsonify({"token": token, "player_id": player.player_id}), 201


@authorization_routes.route("/check_login", methods=["GET"])
@limiter.limit("10 per minute")
def check_login():
    token = request.headers['Authorization']

    if not token:
        return jsonify({"error": "Missing token", "details": "A valid token is missing"}), 400

    player = jwt.decode(token, api.config['SECRET_KEY'], algorithms=['HS256'])

    return jsonify({"message": "Player is logged in: " + str(player["player_id"])}), 200
