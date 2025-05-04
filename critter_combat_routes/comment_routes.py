from flask import Blueprint, request, jsonify

from config import db
from critter_combat_routes.authorization_wrapper import authorization_wrapper
from critter_combat_utils.database import Comment
from critter_combat_utils.utils import comment_to_response

comment_routes = Blueprint("comment_routes", __name__)


@comment_routes.route("/get_page_comments", methods=["GET"])
@authorization_wrapper
def get_page_comments(player):
    page = int(request.args["page"] if "page" in request.args else 0)
    per_page = int(request.args["per_page"] if "per_page" in request.args else 10)
    sort_type = request.args["sort_type"] if "sort_type" in request.args else "recent"

    if "level_id" not in request.args:
        return jsonify({"error": "Parameter required", "details": "level_id query parameter required"}), 400

    level_id = int(request.args["level_id"])

    comments = []
    comments_obj = Comment.query.filter_by(level_id=level_id)

    if sort_type == "recent":
        comments = comments_obj.order_by(Comment.comment_id.desc()).offset(page * per_page).limit(per_page).all()
    if sort_type == "likes":
        comments = comments_obj.order_by(Comment.likes.desc()).offset(page * per_page).limit(per_page).all()

    comments_count = comments_obj.count()

    return jsonify({"count": comments_count, "data": list(map(comment_to_response, comments))}), 200


@comment_routes.route("/get_page_player_comments", methods=["GET"])
@authorization_wrapper
def get_page_player_comments(player):
    page = int(request.args["page"] if "page" in request.args else 0)
    per_page = int(request.args["per_page"] if "per_page" in request.args else 10)
    sort_type = request.args["sort_type"] if "sort_type" in request.args else "recent"

    comments = []
    comments_obj = Comment.query.filter_by(player_id=int(request.args["other_id"]) if "other_id" in request.args else player["player_id"])

    if sort_type == "recent":
        comments = comments_obj.order_by(Comment.comment_id.desc()).offset(page * per_page).limit(per_page).all()
    if sort_type == "likes":
        comments = comments_obj.order_by(Comment.likes.desc()).offset(page * per_page).limit(per_page).all()

    comments_count = comments_obj.count()

    return jsonify({"count": comments_count, "data": list(map(comment_to_response, comments))}), 200


@comment_routes.route("/like_comment", methods=["POST"])
@authorization_wrapper
def like_comment(player):
    data = request.json

    comment_to_like = Comment.query.filter_by(comment_id=data["comment_id"]).first()

    if not comment_to_like:
        return jsonify({"error": "Comment dont exist", "details": "Comment dont exist"}), 400

    comment_to_like.likes += 1 if data["is_like"] else -1

    db.session.commit()

    return jsonify({"message": "Comment is " + ("liked" if data["is_like"] else "disliked")}), 201
