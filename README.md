# FAQ Bot

A chatbot that answers questions using a FAQ file. It runs in two ways: as a terminal chat app, or as a web API built with FastAPI.

## Features

- Answers questions by finding keywords from `faq.txt`
- Shows the full chat history and the total message count when the user types "quit"
- Saves every message to `log.json` with its time, role, and content
- Remembers previous conversations by loading `log.json` when the bot starts
- Coloured terminal output using the `rich` library
- Web API with endpoints to ask questions, list the FAQ keywords, and view the chat history
- Input validation with Pydantic: empty or overly long questions are rejected with a `422` error before they reach the bot

## How to run

1. Clone the repo and enter the folder
```bash
git clone https://github.com/JasonToh9672/faq-bot
cd faq-bot
```
2. Create a virtual environment
```bash
python -m venv .venv
```
3. Activate it

**For Windows**
```bash
.venv\Scripts\activate
```
**For Mac or Linux**
```bash
source .venv/bin/activate
```
4. Install the packages and run
```bash
python -m pip install -r requirements.txt
python main.py
```

## Run as an API

After steps 1–4 above, start the API server:
```bash
fastapi dev api.py
```
Then open http://127.0.0.1:8000/docs in your browser to try the endpoints.

| Method | Endpoint | Description |
|---|---|---|
| POST | `/ask` | Ask a question and get an answer |
| GET | `/faq` | List all the keywords the bot knows |
| GET | `/history` | View the chat history |

Example request body for `/ask`:
```json
{
  "question": "How do I get a refund?"
}
```

Example response:
```json
{
  "question": "How do I get a refund?",
  "answer": "You can request a refund within 7 days of purchase."
}
```

## Known limitations

- **Shared history:** all API users share one chat history, so users can see each other's questions.
- **No persistence for the API:** the API's chat history is stored in memory, so it is lost when the server restarts.
- **Simple keyword matching:** the bot matches text inside words, not whole words, so it can give wrong answers (e.g. "ladybug" matches "bug").

**Planned improvements:** a database so the history survives restarts, and user login so each user only sees their own history.

## What I learned

- How to split code into module files and import them
- That keyword matching is weak because it matches text inside words, not whole words (e.g. "bug" also matches "ladybug")
- How to save and load data with JSON instead of plain text, so it can be read back as Python dicts
- How FastAPI decides where each parameter comes from: the URL path, the query string, or the JSON body (a Pydantic model)
- That with Pydantic validation, invalid input gets a `422` response and my function never runs, so I don't need to write the checks myself