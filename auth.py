import os
from datetime import datetime, timedelta, timezone

import jwt
from dotenv import load_dotenv
from pwdlib import PasswordHash

load_dotenv()                                        # read .env (for SECRET_KEY)

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

password_hash = PasswordHash.recommended()           # Argon2
DUMMY_HASH = password_hash.hash("dummy-password")    # for the "no such user" case (same timing)


def get_secret_key():
    secret_key = os.environ.get("SECRET_KEY")
    if secret_key is None:
        raise RuntimeError("SECRET_KEY is not set. Copy .env.example to .env and fill it in.")
    return secret_key


def create_access_token(user_id):
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {"sub": str(user_id), "exp": expire}    # the user's ID, as TEXT, because id is UNIQUE with GENERATED ALWAYS AS IDENTITY
    return jwt.encode(payload, get_secret_key(), algorithm=ALGORITHM)   # and when decode, payload must be string, so we str(user_id) when encode
