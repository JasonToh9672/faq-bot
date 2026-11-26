from fastapi import Depends, FastAPI, HTTPException
from pydantic import BaseModel, Field

import db                                                  # the whole module: db.create_user(...)
from auth import DUMMY_HASH, create_access_token, get_current_user, password_hash
from faq_bot import FAQBot

bot = FAQBot("faq.txt", "api")

app = FastAPI()


class AskRequest(BaseModel):
    question: str = Field(min_length=1, max_length=300)


class SignupRequest(BaseModel):
    username: str = Field(min_length=3, max_length=30)
    password: str = Field(min_length=8, max_length=100)


class LoginRequest(BaseModel):
    username: str
    password: str


@app.post("/signup")
def signup(request: SignupRequest):
    hashed_password = password_hash.hash(request.password)            # hash first, never store the password
    user_id = db.create_user(request.username, hashed_password)        # save in PostgreSQL
    if user_id is None:                                                # UNIQUE said no
        raise HTTPException(status_code=409, detail="Username already taken")
    return {"id": user_id, "username": request.username}


@app.post("/login")
def login(request: LoginRequest):
    user = db.get_user_by_username(request.username)                   # from PostgreSQL now
    if user is None:
        password_hash.verify(request.password, DUMMY_HASH)
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    if not password_hash.verify(request.password, user["hashed_password"]):
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    token = create_access_token(user["id"])                            # the ID goes into the token
    return {"access_token": token, "token_type": "bearer"}

@app.get("/me")
def read_me(current_user: dict = Depends(get_current_user)):
    return current_user                                     # {"id": ..., "username": ...}, no hash


@app.post("/ask")
def create_ask(ask: AskRequest, current_user: dict = Depends(get_current_user)):
    answer = bot.find_answer(ask.question)                  # ONLY find the answer (no memory history)
    db.add_message(current_user["id"], "user", ask.question)        # save the question for THIS user
    db.add_message(current_user["id"], "assistant", answer)         # save the answer for THIS user
    return {"question": ask.question, "answer": answer}


@app.get("/faq")
def list_faq():
    return list(bot.faq)                                    # public: no Depends
# because faq already is load_faq(faq_path) and list() already filter only dict keys

@app.get("/history")
def list_history(current_user: dict = Depends(get_current_user)):
    return db.get_messages(current_user["id"])              # only THIS user's messages



