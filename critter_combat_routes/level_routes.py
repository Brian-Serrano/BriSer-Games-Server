import json
import os
import re

import bleach
from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename

import config
from config import db, api
from critter_combat_routes.authorization_wrapper import authorization_wrapper
from critter_combat_utils.database import Level, Comment
from critter_combat_utils.utils import level_to_response, increase_version, check_for_bad_word, is_number

level_routes = Blueprint("level_routes", __name__)


@level_routes.route("/upload_created_level", methods=["POST"])
@authorization_wrapper
def upload_created_level(player):
    data = json.loads(request.form["level_metadata"])
    level_data = request.files["level"]

    data["level_name"] = bleach.clean(data["level_name"].strip())
    data["level_description"] = bleach.clean(data["level_description"].strip())

    # level name validation
    if len(data["level_name"]) == 0:
        return jsonify({"error": "Invalid level name", "details": "Level name is empty"}), 400
    if len(data["level_name"]) > 20:
        return jsonify({"error": "Invalid level name", "details": "Level name should be up to 20 characters"}), 400
    if check_for_bad_word(data["level_name"]):
        return jsonify({"error": "Invalid level name", "details": "Level name contains inappropriate words"}), 400
    if not re.match(config.ALNUM_SP_PATTERN, data["level_name"]):
        return jsonify({"error": "Invalid level name", "details": "Level name contains invalid characters"}), 400

    # level description validation
    if len(data["level_description"]) > 200:
        return jsonify({"error": "Invalid level description", "details": "Level description should be up to 200 characters"}), 400
    if check_for_bad_word(data["level_description"]):
        return jsonify({"error": "Invalid level description", "details": "Level description contains inappropriate words"}), 400
    if not re.match(config.DESC_VAL_PATTERN, data["level_description"]):
        return jsonify({"error": "Invalid level description", "details": "Level description contains invalid characters"}), 400

    # difficulty validation
    if data["difficulty"] not in ["EASY", "NORMAL", "HARD", "INSANE", "EXTREME"]:
        return jsonify({"error": "Invalid difficulty", "details": "Difficulty is invalid"}), 400

    # level verified validation
    if not data["level_verified"]:
        return jsonify({"error": "Level is unverified", "details": "Level is unverified, how you have been able to upload it"}), 400

    if data["coins"] > 10:
        return jsonify({"error": "Coins exceed limit", "details": "Coins should be up to 10"}), 400

    if data["diamonds"] > 3:
        return jsonify({"error": "Diamonds exceed limit", "details": "Diamonds should be up to 3"}), 400

    if data["level_id"] != 0:  # level is already uploaded
        existing_level = Level.query.filter_by(level_id=data["level_id"]).first()

        if not existing_level:
            return jsonify({"error": "Level dont exists", "details": "Level dont exists, how did you make the level marked as uploaded even not"}), 400

        if data["level_name"] != existing_level.level_name:
            return jsonify({"error": "Level renamed", "details": "Level cannot be renamed after it is uploaded"}), 400

        if data["difficulty"] != existing_level.difficulty:
            return jsonify({"error": "Difficulty changed", "details": "You cannot change the difficulty of level after it is uploaded"}), 400

        existing_level.level_description = data["level_description"]
        existing_level.coins = data["coins"]
        existing_level.diamonds = data["diamonds"]
        existing_level.version = increase_version(existing_level.version)

        level_file_name = secure_filename(str(existing_level.level_id) + ".cclvl")

        with open(os.path.join(api.config['CRITTER_COMBAT_LEVELS_PATH'], level_file_name), 'wb') as file:
            while chunk := level_data.stream.read(8192):
                file.write(chunk)

        db.session.commit()

        return jsonify({"version": existing_level.version, "level_id": existing_level.level_id}), 201

    else:  # level is not uploaded yet
        new_level = Level(
            level_name=data["level_name"],
            level_description=data["level_description"],
            difficulty=data["difficulty"],
            creator_id=player["player_id"],
            coins=data["coins"],
            diamonds=data["diamonds"]
        )

        db.session.add(new_level)
        db.session.commit()

        level_file_name = secure_filename(str(new_level.level_id) + ".cclvl")

        with open(os.path.join(api.config['CRITTER_COMBAT_LEVELS_PATH'], level_file_name), 'wb') as file:
            while chunk := level_data.stream.read(8192):
                file.write(chunk)

        return jsonify({"version": new_level.version, "level_id": new_level.level_id}), 201


@level_routes.route("/download_online_level", methods=["GET"])
@authorization_wrapper
def download_online_level(player):
    level_id = request.args["level_id"]

    if not is_number(level_id):
        raise TypeError()

    level = Level.query.filter_by(level_id=int(level_id)).first()

    if not level:
        return jsonify({"error": "Level dont exist", "details": "Level dont exist"}), 400

    level.downloads += 1

    file_name = secure_filename(level_id + ".cclvl")
    file_full_name = os.path.join(api.config['CRITTER_COMBAT_LEVELS_PATH'], file_name)

    def generate():
        with open(file_full_name, 'rb') as file:
            while chunk := file.read(8192):
                yield chunk

    db.session.commit()

    return generate(), {"Content-Type": "application/octet-stream", "Content-Length": os.path.getsize(file_full_name)}


@level_routes.route("/like_level", methods=["POST"])
@authorization_wrapper
def like_level(player):
    data = request.json

    level_to_like = Level.query.filter_by(level_id=data["level_id"]).first()

    if not level_to_like:
        return jsonify({"error": "Level dont exist", "details": "Level dont exist"}), 400

    level_to_like.likes += 1 if data["is_like"] else -1

    db.session.commit()

    return jsonify({"message": "Level is " + ("liked" if data["is_like"] else "disliked")}), 201


@level_routes.route("/comment_on_level", methods=["POST"])
@authorization_wrapper
def comment_on_level(player):
    data = request.json

    data["description"] = bleach.clean(data["description"].strip())

    # comment validation
    if len(data["description"]) == 0:
        return jsonify({"error": "Invalid comment", "details": "Comment is empty"}), 400
    if len(data["description"]) > 100:
        return jsonify({"error": "Invalid comment", "details": "Comment should be up to 100 characters"}), 400
    if check_for_bad_word(data["description"]):
        return jsonify({"error": "Invalid comment", "details": "Comment contains inappropriate words"}), 400
    if not re.match(config.DESC_VAL_PATTERN, data["description"]):
        return jsonify({"error": "Invalid comment", "details": "Comment contains invalid characters"}), 400

    new_comment = Comment(
        level_id=data["level_id"],
        player_id=player["player_id"],
        comment_description=data["description"]
    )

    db.session.add(new_comment)
    db.session.commit()

    return jsonify({"message": "Comment sent."}), 201


@level_routes.route("/get_page_online_levels", methods=["GET"])
@authorization_wrapper
def get_page_online_levels(player):
    page = int(request.args["page"] if "page" in request.args else 0)
    per_page = int(request.args["per_page"] if "per_page" in request.args else 10)
    sort_type = request.args["sort_type"] if "sort_type" in request.args else "recent"

    levels = []
    levels_obj = apply_filter(request.args, Level.query, "search_query", "is_rated", "difficulty")

    if sort_type == "downloads":
        levels = levels_obj.order_by(Level.downloads.desc()).offset(page * per_page).limit(per_page).all()
    if sort_type == "likes":
        levels = levels_obj.order_by(Level.likes.desc()).offset(page * per_page).limit(per_page).all()
    if sort_type == "recent":
        levels = levels_obj.order_by(Level.level_id.desc()).offset(page * per_page).limit(per_page).all()

    levels_count = levels_obj.count()

    return jsonify({"count": levels_count, "data": list(map(level_to_response, levels))}), 200


@level_routes.route("/get_page_player_levels", methods=["GET"])
@authorization_wrapper
def get_page_player_levels(player):
    page = int(request.args["page"] if "page" in request.args else 0)
    per_page = int(request.args["per_page"] if "per_page" in request.args else 10)

    # if there is other id args provided, that means player visit other player's levels, else player visit his uploaded levels
    levels_obj = Level.query.filter_by(creator_id=int(request.args["other_id"]) if "other_id" in request.args else player["player_id"])
    levels = levels_obj.order_by(Level.level_id.desc()).offset(page * per_page).limit(per_page).all()
    levels_count = levels_obj.count()

    return jsonify({"count": levels_count, "data": list(map(level_to_response, levels))}), 200


def apply_filter(query_args, levels, search_query, is_rated, difficulty):
    if search_query in query_args:
        levels = levels.filter(Level.level_name.ilike(f"%{query_args["search_query"]}%"))

    if is_rated in query_args:
        levels = levels.filter_by(is_rated=True)

    if difficulty in query_args:
        levels = levels.filter_by(difficulty=query_args["difficulty"])

    return levels
