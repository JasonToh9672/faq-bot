# FAQ Bot

A terminal chatbot that answers user questions using a FAQ file.

## Features

- Answers questions by finding keywords from `faq.txt`
- Shows the full chat history and the total message count when the user types "quit"
- Saves every message to `log.json` with its time, role, and content
- Coloured terminal output using the `rich` library

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

## What I learned

- How to split code into module files and import them
- That keyword matching is weak because it matches text inside words, not whole words (e.g. “bug” also matches “ladybug”)