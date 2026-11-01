from faq_bot import FAQBot
from fastapi import FastAPI,HTTPException
from pydantic import BaseModel ,Field

bot = FAQBot("faq.txt", "api")

class Askrequest (BaseModel):
    question: str = Field(min_length=1, max_length=300)

app = FastAPI()

@app.post("/ask")
def create_ask(ask: Askrequest):
    answer = bot.ask(ask.question)
    return {"question": ask.question, "answer": answer} # return in dictionary and fastapi will convert into JSON

@app.get("/faq")
def list_faq():
    return list(bot.faq) # because faq already is load_faq(faq_path) and list() already filter only dict keys

@app.get("/history")
def list_history():
    return bot.history.messages


