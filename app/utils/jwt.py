from jose import jwt, JWTError
from datetime import datetime, timedelta
from dotenv import load_dotenv
import os


load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")


def create_access_token(data: dict):
    to_encode = data.copy()

    expire = datetime.utcnow() + timedelta(days=7)

    to_encode.update({
        "exp": expire
    })

    return jwt.encode(
        to_encode,
        SECRET_KEY,
        algorithm=ALGORITHM
    )


def decode_access_token(token: str) -> dict:
    """
    Decodifica e valida um token JWT.
    Levanta jose.JWTError se o token for inválido, malformado ou expirado.
    """
    return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])