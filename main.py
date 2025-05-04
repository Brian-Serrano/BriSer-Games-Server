from json import JSONDecodeError

import jwt
from sqlalchemy.exc import IntegrityError, OperationalError

from config import api, db
import critter_combat_routes as ccr
import critter_combat_utils as ccu

api.register_blueprint(ccr.player_routes, url_prefix="/player_routes")
api.register_blueprint(ccr.level_routes, url_prefix="/level_routes")
api.register_blueprint(ccr.comment_routes, url_prefix="/comment_routes")
api.register_blueprint(ccr.authorization_routes, url_prefix="/authorization_routes")

api.register_error_handler(jwt.ExpiredSignatureError, ccu.handle_jwt_expired_signature_error)
api.register_error_handler(jwt.InvalidTokenError, ccu.handle_jwt_invalid_token_error)
api.register_error_handler(IntegrityError, ccu.handle_integrity_error)
api.register_error_handler(OperationalError, ccu.handle_operational_error)
api.register_error_handler(JSONDecodeError, ccu.handle_json_error)
api.register_error_handler(KeyError, ccu.handle_key_error)
api.register_error_handler(TypeError, ccu.handle_type_error)
api.register_error_handler(ValueError, ccu.handle_value_error)
api.register_error_handler(Exception, ccu.handle_general_error)


if __name__ == '__main__':

    with api.app_context():
        db.create_all()

    api.run(debug=True)
