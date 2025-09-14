import random

import bcrypt

from config import api
from td_rubix_utils.database import db, Player
# from room_escape_utils.database import db, Player

# creates 200 test users for room escape database
def seed_re_players(n=200):
    with api.app_context():
        players = []
        for i in range(n):
            player = Player(
                player_name=f"PlayerTest{i+1}",
                email=f"player{i+1}@gmail.com",
                password=bcrypt.hashpw(f"playertest{i+1}".encode(), bcrypt.gensalt()).decode(),
                total_coins=random.randint(0, 10000),
                level=random.randint(0, 200),
                high_score=random.randint(0, 10000)
            )
            players.append(player)

        db.session.bulk_save_objects(players)
        db.session.commit()
        print(f"✅ {n} players added to database.")

# creates 200 test users for 2d rubix database
def seed_tr_players(n=200):
    with api.app_context():
        players = []
        for i in range(n):
            player = Player(
                player_name=f"PlayerTest{i+1}",
                email=f"player{i+1}@gmail.com",
                password=bcrypt.hashpw(f"playertest{i+1}".encode(), bcrypt.gensalt()).decode(),
                level=random.randint(0, 200)
            )
            players.append(player)

        db.session.bulk_save_objects(players)
        db.session.commit()
        print(f"✅ {n} players added to database.")

if __name__ == "__main__":
    seed_tr_players(200)