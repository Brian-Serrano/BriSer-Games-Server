from flask import jsonify

from config import db


def handle_jwt_expired_signature_error(e):
    return jsonify({"error": "Token expired", "details": str(e)}), 400


def handle_jwt_invalid_token_error(e):
    return jsonify({"error": "Invalid Token", "details": str(e)}), 400


def handle_integrity_error(e):
    db.session.rollback()
    return jsonify({"error": "Database integrity error", "details": str(e)}), 400


def handle_operational_error(e):
    db.session.rollback()
    return jsonify({"error": "Database connection error", "details": str(e)}), 500


def handle_json_error(e):
    return jsonify({"error": "Invalid JSON payload", "details": str(e)}), 400


def handle_key_error(e):
    return jsonify({"error": "Missing key", "details": str(e)}), 400


def handle_type_error(e):
    return jsonify({"error": "Type error", "details": str(e)}), 400


def handle_value_error(e):
    return jsonify({"error": "Invalid value", "details": str(e)}), 400


def handle_general_error(e):
    db.session.rollback()
    return jsonify({"error": "Internal server error", "details": str(e)}), 500
