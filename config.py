import os

from dotenv import load_dotenv
from flask import Flask
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_sqlalchemy import SQLAlchemy
from supabase import create_client

load_dotenv()

api = Flask(__name__)

api.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DATABASE_URI")

api.config['SECRET_KEY'] = "Uttog at nagsasalsal mga kapitbahay ko."
api.config['API_KEY'] = "Bobo mga kapitbahay ko."

CRITTER_COMBAT_LEVELS_BUCKET_NAME = "critter_combat_levels"
CRITTER_COMBAT_PLAYER_DATA_BUCKET_NAME = "critter_combat_player_data"
BLADE_DEFENSE_PLAYER_DATA_BUCKET_NAME = "blade_defense_player_data"
ROOM_ESCAPE_PLAYER_DATA_BUCKET_NAME = "room_escape_player_data"
TD_RUBIX_PLAYER_DATA_BUCKET_NAME = "td_rubix_player_data"
CUBE_JUMP_PLAYER_DATA_BUCKET_NAME = "cube_jump_player_data"
FORTY_ONE_PLAYER_DATA_BUCKET_NAME = "forty_one_player_data"

api.config['UPLOAD_MAX_SIZE'] = 100

ALNUM_PATTERN = r"^[\w-]+$"
ALNUM_SP_PATTERN = r"^[A-Za-z 0-9]*$"
EMAIL_PATTERN = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
DESC_VAL_PATTERN = r"""^[A-Za-z0-9!@#$%&*()\-_=+{\[}\]|\\`~:;'",./?\s]*$"""
DIGIT_PATTERN = r"^\d+$"

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

db = SQLAlchemy(api)

limiter = Limiter(
    get_remote_address,
    storage_uri=os.getenv("REDIS_URL"),
    app=api,
    default_limits=["50 per minute"]
)