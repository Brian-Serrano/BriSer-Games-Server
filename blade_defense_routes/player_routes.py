import os

from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename

from blade_defense_routes.authorization_wrapper import authorization_wrapper
from config import api, limiter, supabase, BLADE_DEFENSE_PLAYER_DATA_BUCKET_NAME

player_routes = Blueprint("bd_player_routes", __name__)


@player_routes.route("/save_player_data", methods=["POST"])
@limiter.limit("10 per minute")
@authorization_wrapper
def save_player_data(current_player):
    file_name = secure_filename(str(current_player["player_id"]) + ".bd")

    data_file = request.files["data"]

    file_bytes = data_file.read()

    res = supabase.storage.from_(BLADE_DEFENSE_PLAYER_DATA_BUCKET_NAME).upload(
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
    file_name = secure_filename(str(current_player["player_id"]) + ".bd")

    res = supabase.storage.from_(BLADE_DEFENSE_PLAYER_DATA_BUCKET_NAME).download(file_name)

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