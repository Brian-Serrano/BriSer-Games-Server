import os.path

from flask import Blueprint, request, jsonify, Response
from werkzeug.utils import secure_filename

from config import db, api, supabase, CRITTER_COMBAT_PLAYER_DATA_BUCKET_NAME, limiter
from critter_combat_routes.authorization_wrapper import authorization_wrapper
from critter_combat_utils.database import Player

player_routes = Blueprint("cc_player_routes", __name__)


@player_routes.route("/save_player_profile", methods=["POST"])
@limiter.limit("10 per minute")
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
@limiter.limit("10 per minute")
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
@limiter.limit("10 per minute")
@authorization_wrapper
def save_player_data(current_player):
    file_name = secure_filename(str(current_player["player_id"]) + ".playerdata")

    data_file = request.files["data"]

    file_bytes = data_file.read()

    res = supabase.storage.from_(CRITTER_COMBAT_PLAYER_DATA_BUCKET_NAME).upload(
        file_name,
        file_bytes,
        {
            "content-type": data_file.mimetype,
            "upsert": "true"
        }
    )

    if isinstance(res, dict) and "error" in res:
        return jsonify({"error": "Supabase Error", "details": res["error"]["message"]}), 400

    return jsonify({"message": "Your data has successfully backed up"}), 201


@player_routes.route("/load_player_data", methods=["GET"])
@limiter.limit("10 per minute")
@authorization_wrapper
def load_player_data(current_player):
    file_name = secure_filename(str(current_player["player_id"]) + ".playerdata")

    res = supabase.storage.from_(CRITTER_COMBAT_PLAYER_DATA_BUCKET_NAME).download(file_name)

    if res is None or isinstance(res, dict) and "error" in res:
        return jsonify({"error": "Supabase Error", "details": "File not found"}), 404

    def generate():
        chunk_size = 8192
        for i in range(0, len(res), chunk_size):
            yield res[i: i + chunk_size]

    return generate(), {
        "Content-Type": "application/zip",
        "Content-Length": str(len(res)),
        "Content-Disposition": f'attachment; filename="{file_name}"'
    }
