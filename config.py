from flask import Flask
from flask_sqlalchemy import SQLAlchemy

api = Flask(__name__)

api.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///default.db"
api.config['SQLALCHEMY_BINDS'] = {
    "critter_combat": "sqlite:///critter_combat_levels.db"
}

api.config['SECRET_KEY'] = "Uttog at nagsasalsal mga kapitbahay ko."
api.config['API_KEY'] = "Bobo mga kapitbahay ko."

api.config['CRITTER_COMBAT_LEVELS_PATH'] = "critter_combat_levels"
api.config['CRITTER_COMBAT_PLAYER_DATA_PATH'] = "critter_combat_player_data"

api.config['ALLOWED_CRITTER_COMBAT_FILES'] = {"playerdata", "lvl"}
api.config['UPLOAD_MAX_SIZE'] = 100

ALNUM_PATTERN = r"^[\w-]+$"
ALNUM_SP_PATTERN = r"^[A-Za-z 0-9]*$"
EMAIL_PATTERN = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
DESC_VAL_PATTERN = r"""^[A-Za-z0-9!@#$%&*()\-_=+{\[}\]|\\`~:;'",./?\s]*$"""
DIGIT_PATTERN = r"^\d+$"

db = SQLAlchemy(api)
