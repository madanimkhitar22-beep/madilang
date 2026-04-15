import jwt
import datetime


class JWTEngine:
    """
    Generates and verifies JWT tokens for MadiLang backend
    """

    def __init__(self, secret="MADI_SECRET_KEY"):
        self.secret = secret

    def generate_token(self, payload):
        """
        Create JWT token for authenticated user
        """
        payload.update({
            "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=24)
        })

        token = jwt.encode(payload, self.secret, algorithm="HS256")
        return token

    def verify_token(self, token):
        """
        Validate JWT token
        """
        try:
            decoded = jwt.decode(token, self.secret, algorithms=["HS256"])
            return {
                "valid": True,
                "data": decoded
            }
        except jwt.ExpiredSignatureError:
            return {"valid": False, "error": "Token expired"}
        except jwt.InvalidTokenError:
            return {"valid": False, "error": "Invalid token"}
