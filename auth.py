import os
from datetime import datetime, timedelta, timezone

import jwt
from dotenv import load_dotenv
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pwdlib import PasswordHash

import db

bearer_scheme = HTTPBearer()    # reads "Authorization: Bearer ..." (check 1 - if authorization is None or not authorization.startswith("Bearer ")) and adds the Authorize button

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

# How a logged-in request works (no password needed after login):
#   1st time: /login checks the password against the stored hash → makes a token with "sub" = the user's id (as text)
#   After that, every request sends "Authorization: Bearer <token>":
#     check 1: HTTPBearer         → is there a Bearer token?                  (no → 401 "Not authenticated")
#     check 2: jwt.decode         → is the signature real and not expired?            (no → 401)
#     check 3: db.get_user_by_id  → int(payload["sub"]) → does that user still exist? (no → 401)
#   A valid token = proof the person ALREADY typed the right password at login, so no password check here.
#   Why the id, not the username: ids are never reused, so a token can't work for a different person
#   who later signs up with the same username.

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme)):
    token = credentials.credentials     # the token part, without "Bearer "
    try:
        payload = jwt.decode(token, get_secret_key(), algorithms=[ALGORITHM])  # check 2: stamp + expiry
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    user = db.get_user_by_id(int(payload["sub"]))                            # check 3: does this user exist?
    if user is None:        # convert it to int and pass, so the database query can use when writing WHERE id = %s (int,)
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    return user

