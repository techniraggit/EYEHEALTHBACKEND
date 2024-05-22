import redis
from jwt.exceptions import DecodeError, ExpiredSignatureError
from datetime import datetime
import jwt


class SessionManager:
    def __init__(self, host="localhost", port=6379, db=0):
        self.redis_client = redis.Redis(host=host, port=port, db=db)

    def get_token_expiry(self):
        return 3600
        # try:
        #     decoded_token = jwt.decode(jwt_token, options={"verify_signature": False})
        #     time_diff = decoded_token["exp"] - datetime.now().timestamp()
        #     if time_diff > 0:
        #         return int(time_diff)
        #     return 0
        # except ExpiredSignatureError:
        #     print("JWT has expired")
        #     return 0
        # except DecodeError:
        #     print("Invalid JWT token")
        #     return 0
        # except KeyError:
        #     print("Token does not contain 'exp' claim")
        #     return 0

    def store_session_token(self, user_id, session_token):
        key = f"session:{user_id}"
        expiry_seconds = self.get_token_expiry()
        self.redis_client.setex(key, expiry_seconds, session_token)

    def get_session_token(self, user_id):
        key = f"session:{user_id}"
        session_token = self.redis_client.get(key)
        return session_token.decode() if session_token else None
