from flask import Blueprint, request, jsonify
from sqlalchemy.sql.expression import case
from werkzeug.utils import secure_filename

from td_rubix_routes.authorization_wrapper import authorization_wrapper
from config import db, limiter, supabase, TD_RUBIX_PLAYER_DATA_BUCKET_NAME
from td_rubix_utils.database import Player
from td_rubix_utils.utils import leaderboard_to_response

player_routes = Blueprint("tr_player_routes", __name__)


@player_routes.route("/save_player_data", methods=["POST"])
@limiter.limit("10 per minute")
@authorization_wrapper
def save_player_data(current_player):
    file_name = secure_filename(str(current_player["player_id"]) + ".2r")

    data_file = request.files["data"]

    file_bytes = data_file.read()

    res = supabase.storage.from_(TD_RUBIX_PLAYER_DATA_BUCKET_NAME).upload(
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
    file_name = secure_filename(str(current_player["player_id"]) + ".2r")

    res = supabase.storage.from_(TD_RUBIX_PLAYER_DATA_BUCKET_NAME).download(file_name)

    if res is None or isinstance(res, dict) and "error" in res:
        return jsonify({"error": "Supabase Error", "details": "File not found"}), 404

    def generate():
        chunk_size = 8192
        for i in range(0, len(res), chunk_size):
            yield res[i: i + chunk_size]

    return generate(), {
        "Content-Type": "application/octet-stream",
        "Content-Length": str(len(res)),
        "Content-Disposition": f'attachment; filename="{file_name}"'
    }

@player_routes.route("/save_leaderboard_data", methods=["POST"])
@limiter.limit("10 per minute")
@authorization_wrapper
def save_leaderboard_data(current_player):
    data = request.json

    player = Player.query.filter_by(player_id=current_player["player_id"]).first()

    if not player:
        return jsonify({"error": "Player dont exist", "details": "Player dont exist"}), 400

    player.level = int(data["level"])

    db.session.commit()

    return jsonify({"message": "Leaderboard data saved."}), 201

@player_routes.route("/get_leaderboard", methods=["GET"])
@limiter.limit("50 per minute")
@authorization_wrapper
def get_leaderboard(current_player):
    around = request.args.get("around", "false").lower() in ("true", "1", "yes")

    player = Player.query.filter_by(player_id=current_player["player_id"]).first()

    if not player:
        return jsonify({"error": "Player dont exist", "details": "Player dont exist"}), 400

    if around:
        rank, response = get_leaderboard_around(player.level, Player.level, current_player["player_id"])
        return jsonify({"rank": rank, "leaderboard": response}), 200
    else:
        rank, response = get_top_50_leaderboard(player.level, Player.level, current_player["player_id"])
        return jsonify({"rank": rank, "leaderboard": response}), 200

def get_leaderboard_around(value, column, player_id):
    total_players = Player.query.filter(column > 0).count()
    higher_value = Player.query.filter(column > value).count()
    rank = higher_value + 1

    window = 25
    if rank <= window:
        start_rank = 1
        end_rank = min(50, total_players)
    elif rank > total_players - window:
        start_rank = max(1, total_players - 49)
        end_rank = total_players
    else:
        start_rank = rank - window
        end_rank = rank + (49 - window)

    players = (Player.query.filter(column > 0)
               .order_by(column.desc(), case((Player.player_id == player_id, 0), else_=1))
               .offset(start_rank - 1)
               .limit(end_rank - start_rank + 1).all())

    return rank, [leaderboard_to_response(x, i) for i, x in enumerate(players, start=start_rank)]

def get_top_50_leaderboard(value, column, player_id):
    higher_value = Player.query.filter(column > value).count()
    rank = higher_value + 1

    players = (Player.query.filter(column > 0)
               .order_by(column.desc(), case((Player.player_id == player_id, 0), else_=1))
               .limit(50).all())

    return rank, [leaderboard_to_response(x, i + 1) for i, x in enumerate(players)]