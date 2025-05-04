import os.path

from flask import Blueprint, request, jsonify, Response
from werkzeug.utils import secure_filename

from config import db, api
from critter_combat_routes.authorization_wrapper import authorization_wrapper
from critter_combat_utils.database import Player

player_routes = Blueprint("player_routes", __name__)


@player_routes.route("/save_player_profile", methods=["POST"])
@authorization_wrapper
def save_player_profile(current_player):
    data = request.json

    player = Player.query.filter_by(player_id=current_player["player_id"]).first()

    if not player:
        return jsonify({"error": "Player dont exist", "details": "Player dont exist"}), 400

    player.coins_collected = data["coins_collected"]
    player.total_coins_collected = data["total_coins_collected"]
    player.diamonds_collected = data["diamonds_collected"]
    player.total_diamonds_collected = data["total_diamonds_collected"]
    player.attempts = data["attempts"]
    player.time = data["time"]
    player.main_levels_completed = data["main_levels_completed"]
    player.total_levels_completed = data["total_levels_completed"]
    player.players_owned = data["players_owned"]
    player.weapons_owned = data["weapons_owned"]

    db.session.commit()

    return jsonify({"message": "Profile data synced."}), 201


@player_routes.route("/load_player_profile", methods=["GET"])
@authorization_wrapper
def load_player_profile(current_player):
    player = Player.query.filter_by(player_id=int(request.args["other_id"]) if "other_id" in request.args else current_player["player_id"]).first()

    if not player:
        return jsonify({"error": "Player dont exist", "details": "Player dont exist"}), 400

    response = {
        "coins_collected": player.coins_collected,
        "total_coins_collected": player.total_coins_collected,
        "diamonds_collected": player.diamonds_collected,
        "total_diamonds_collected": player.total_diamonds_collected,
        "attempts": player.attempts,
        "time": player.time,
        "main_levels_completed": player.main_levels_completed,
        "total_levels_completed": player.total_levels_completed,
        "players_owned": player.players_owned,
        "weapons_owned": player.weapons_owned
    }

    return jsonify(response), 200


@player_routes.route("/save_player_data", methods=["POST"])
@authorization_wrapper
def save_player_data(current_player):
    file_name = secure_filename(str(current_player["player_id"]) + ".playerdata")
    file_full_name = os.path.join(api.config['CRITTER_COMBAT_PLAYER_DATA_PATH'], file_name)

    data_file = request.files["data"]

    with open(file_full_name, 'wb') as file:
        while chunk := data_file.stream.read(8192):
            file.write(chunk)

    return jsonify({"message": "Your data has successfully backed up"}), 201


@player_routes.route("/load_player_data", methods=["GET"])
@authorization_wrapper
def load_player_data(current_player):
    file_name = secure_filename(str(current_player["player_id"]) + ".playerdata")
    file_full_name = os.path.join(api.config['CRITTER_COMBAT_PLAYER_DATA_PATH'], file_name)

    def generate():
        with open(file_full_name, 'rb') as file:
            while chunk := file.read(8192):
                yield chunk

    return generate(), {"Content-Type": "application/zip", "Content-Length": os.path.getsize(file_full_name)}
