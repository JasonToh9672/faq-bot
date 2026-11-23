from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

import db                                                  # the whole module: db.create_user(...)
from auth import DUMMY_HASH, create_access_token, password_hash
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

    
@app.post("/ask")
def create_ask(ask: AskRequest):
    answer = bot.ask(ask.question)
    return {"question": ask.question, "answer": answer} # return in dictionary and fastapi will convert into JSON

@app.get("/faq")
def list_faq():
    return list(bot.faq) # because faq already is load_faq(faq_path) and list() already filter only dict keys

@app.get("/history")
def list_history():
    return bot.history.messages


