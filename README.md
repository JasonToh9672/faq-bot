# FAQ Bot

A terminal chatbot that answers user questions using a FAQ file.

## Features

- Answers questions by finding keywords from `faq.txt`
- Shows the full chat history and the total message count when the user types "quit"
- Saves every message to `log.txt` with its time, role, and content
- Coloured terminal output using the `rich` library

## How to run

```
python -m venv .venv
.venv\Scripts\activate
python -m pip install -r requirements.txt
python main.py
```

## What I learned

- How to split code into module files and import them
- That keyword matching is weak because it matches text inside words, not whole words (e.g. “bug” also matches “ladybug”)