from json import JSONDecodeError

import jwt
from sqlalchemy.exc import IntegrityError, OperationalError

from config import api, db
import blade_defense_routes as bdr
import blade_defense_utils as bdu
import critter_combat_routes as ccr
import critter_combat_utils as ccu
import room_escape_routes as rer
import room_escape_utils as reu
import td_rubix_routes as trr
import td_rubix_utils as tru
import cube_jump_routes as cjr
import cube_jump_utils as cju

api.register_blueprint(ccr.player_routes, url_prefix="/cc_player_routes")
api.register_blueprint(ccr.level_routes, url_prefix="/cc_level_routes")
api.register_blueprint(ccr.comment_routes, url_prefix="/cc_comment_routes")
api.register_blueprint(ccr.authorization_routes, url_prefix="/cc_authorization_routes")

api.register_blueprint(bdr.player_routes, url_prefix="/bd_player_routes")
api.register_blueprint(bdr.authorization_routes, url_prefix="/bd_authorization_routes")

api.register_blueprint(rer.player_routes, url_prefix="/re_player_routes")
api.register_blueprint(rer.authorization_routes, url_prefix="/re_authorization_routes")

api.register_blueprint(trr.player_routes, url_prefix="/tr_player_routes")
api.register_blueprint(trr.authorization_routes, url_prefix="/tr_authorization_routes")

api.register_blueprint(cjr.player_routes, url_prefix="/cj_player_routes")
api.register_blueprint(cjr.authorization_routes, url_prefix="/cj_authorization_routes")

api.register_error_handler(jwt.ExpiredSignatureError, ccu.handle_jwt_expired_signature_error)
api.register_error_handler(jwt.InvalidTokenError, ccu.handle_jwt_invalid_token_error)
api.register_error_handler(IntegrityError, ccu.handle_integrity_error)
api.register_error_handler(OperationalError, ccu.handle_operational_error)
api.register_error_handler(JSONDecodeError, ccu.handle_json_error)
api.register_error_handler(KeyError, ccu.handle_key_error)
api.register_error_handler(TypeError, ccu.handle_type_error)
api.register_error_handler(ValueError, ccu.handle_value_error)
api.register_error_handler(Exception, ccu.handle_general_error)

api.register_error_handler(jwt.ExpiredSignatureError, bdu.handle_jwt_expired_signature_error)
api.register_error_handler(jwt.InvalidTokenError, bdu.handle_jwt_invalid_token_error)
api.register_error_handler(IntegrityError, bdu.handle_integrity_error)
api.register_error_handler(OperationalError, bdu.handle_operational_error)
api.register_error_handler(JSONDecodeError, bdu.handle_json_error)
api.register_error_handler(KeyError, bdu.handle_key_error)
api.register_error_handler(TypeError, bdu.handle_type_error)
api.register_error_handler(ValueError, bdu.handle_value_error)
api.register_error_handler(Exception, bdu.handle_general_error)

api.register_error_handler(jwt.ExpiredSignatureError, reu.handle_jwt_expired_signature_error)
api.register_error_handler(jwt.InvalidTokenError, reu.handle_jwt_invalid_token_error)
api.register_error_handler(IntegrityError, reu.handle_integrity_error)
api.register_error_handler(OperationalError, reu.handle_operational_error)
api.register_error_handler(JSONDecodeError, reu.handle_json_error)
api.register_error_handler(KeyError, reu.handle_key_error)
api.register_error_handler(TypeError, reu.handle_type_error)
api.register_error_handler(ValueError, reu.handle_value_error)
api.register_error_handler(Exception, reu.handle_general_error)

api.register_error_handler(jwt.ExpiredSignatureError, tru.handle_jwt_expired_signature_error)
api.register_error_handler(jwt.InvalidTokenError, tru.handle_jwt_invalid_token_error)
api.register_error_handler(IntegrityError, tru.handle_integrity_error)
api.register_error_handler(OperationalError, tru.handle_operational_error)
api.register_error_handler(JSONDecodeError, tru.handle_json_error)
api.register_error_handler(KeyError, tru.handle_key_error)
api.register_error_handler(TypeError, tru.handle_type_error)
api.register_error_handler(ValueError, tru.handle_value_error)
api.register_error_handler(Exception, tru.handle_general_error)

api.register_error_handler(jwt.ExpiredSignatureError, cju.handle_jwt_expired_signature_error)
api.register_error_handler(jwt.InvalidTokenError, cju.handle_jwt_invalid_token_error)
api.register_error_handler(IntegrityError, cju.handle_integrity_error)
api.register_error_handler(OperationalError, cju.handle_operational_error)
api.register_error_handler(JSONDecodeError, cju.handle_json_error)
api.register_error_handler(KeyError, cju.handle_key_error)
api.register_error_handler(TypeError, cju.handle_type_error)
api.register_error_handler(ValueError, cju.handle_value_error)
api.register_error_handler(Exception, cju.handle_general_error)


if __name__ == '__main__':

    with api.app_context():
        db.create_all()

    api.run()
