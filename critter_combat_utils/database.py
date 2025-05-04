from config import db


class Level(db.Model):
    __bind_key__ = "critter_combat"

    level_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    level_name = db.Column(db.String(20), nullable=False, default="Unnamed 1")
    level_description = db.Column(db.String(200), nullable=False, default="No description provided")
    creator_id = db.Column(db.Integer, db.ForeignKey("player.player_id"), nullable=False)
    version = db.Column(db.String(10), nullable=False, default="1.0")
    difficulty = db.Column(db.String(10), nullable=False, default="NONE")
    downloads = db.Column(db.Integer, nullable=False, default=0)
    likes = db.Column(db.Integer, nullable=False, default=0)
    is_rated = db.Column(db.Boolean, nullable=False, default=False)
    coins = db.Column(db.Integer, nullable=False, default=0)
    diamonds = db.Column(db.Integer, nullable=False, default=0)
    comments = db.relationship("Comment", backref="level", lazy=True)


class Player(db.Model):
    __bind_key__ = "critter_combat"

    player_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    player_name = db.Column(db.String(20), nullable=False, default="Player")
    email = db.Column(db.String(100), nullable=False, default="player@nothing.com")
    password = db.Column(db.String(128), nullable=False, default="player123")
    coins_collected = db.Column(db.Integer, nullable=False, default=0)
    total_coins_collected = db.Column(db.Integer, nullable=False, default=0)
    diamonds_collected = db.Column(db.Integer, nullable=False, default=0)
    total_diamonds_collected = db.Column(db.Integer, nullable=False, default=0)
    attempts = db.Column(db.Integer, nullable=False, default=0)
    time = db.Column(db.Integer, nullable=False, default=0)
    main_levels_completed = db.Column(db.Integer, nullable=False, default=0)
    total_levels_completed = db.Column(db.Integer, nullable=False, default=0)
    players_owned = db.Column(db.Integer, nullable=False, default=0)
    weapons_owned = db.Column(db.Integer, nullable=False, default=0)
    comments = db.relationship("Comment", backref="player", lazy=True)
    levels = db.relationship("Level", backref="player", lazy=True)


class Comment(db.Model):
    __bind_key__ = "critter_combat"

    comment_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    level_id = db.Column(db.Integer, db.ForeignKey("level.level_id"), nullable=False)
    player_id = db.Column(db.Integer, db.ForeignKey("player.player_id"), nullable=False)
    comment_description = db.Column(db.String(300), nullable=False, default="...")
    likes = db.Column(db.Integer, nullable=False, default=0)
