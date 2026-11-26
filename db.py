import os

import psycopg
from dotenv import load_dotenv

load_dotenv()    # runs once, read the .env file when db.py is first loaded, whether it's run directly or imported


def get_database_url():
    database_url = os.environ.get("DATABASE_URL")
    if database_url is None:                     # forgot to make .env, or a typo in the name
        raise RuntimeError("DATABASE_URL is not set. Copy .env.example to .env and fill it in.")
    return database_url


def get_connection():
    return psycopg.connect(get_database_url())   # one connection, using the URL


def create_tables():
    with get_connection() as connection:
        cursor = connection.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
                username TEXT NOT NULL UNIQUE,
                hashed_password TEXT NOT NULL,
                created_at TIMESTAMPTZ NOT NULL DEFAULT now()
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
                user_id INTEGER NOT NULL,
                role TEXT NOT NULL CHECK (role IN ('user', 'assistant')),
                content TEXT NOT NULL,
                created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
                FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
            )
        """)
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_messages_user_id ON messages (user_id)")

def create_user(username, hashed_password):
    try:
        with get_connection() as connection:
            cursor = connection.cursor()
            cursor.execute(
                "INSERT INTO users (username, hashed_password) VALUES (%s, %s) RETURNING id",
                (username, hashed_password),
            )
            return cursor.fetchone()[0]          # the new user's id
    except psycopg.errors.UniqueViolation:       # the username is already taken (UNIQUE)
        return None

def get_user_by_username(username):
    with get_connection() as connection:
        cursor = connection.cursor()
        cursor.execute(
            "SELECT id, username, hashed_password FROM users WHERE username = %s",
            (username,),
        )
        row = cursor.fetchone()          # a tuple like (1, 'toh', '$argon2id$...'), or None
    if row is None:                      # no user with that name
        return None
    return {"id": row[0], "username": row[1], "hashed_password": row[2]}   # tuple → dict

# get_user_by_username → used by /login → NEEDS hashed_password (to verify the typed password)
# get_user_by_id       → used by the guard on every request after login → NO hashed_password, because:
#   - no password is checked there: it was already checked at login, and the token is the ticket
#   - its result becomes current_user, which /me sends straight to the browser
#   Rule: fetch only what that job needs.

def get_user_by_id(user_id):
    with get_connection() as connection:
        cursor = connection.cursor()
        cursor.execute(
            "SELECT id, username FROM users WHERE id = %s",      # NO hashed_password here (on purpose)
            (user_id,),
        )
        row = cursor.fetchone()
    if row is None:
        return None
    return {"id": row[0], "username": row[1]}

def add_message(user_id, role, content):
    with get_connection() as connection:
        cursor = connection.cursor()
        cursor.execute(
            "INSERT INTO messages (user_id, role, content) VALUES (%s, %s, %s)",
            (user_id, role, content),
        )


def get_messages(user_id):
    with get_connection() as connection:
        cursor = connection.cursor()
        cursor.execute(
            "SELECT role, content, created_at FROM messages WHERE user_id = %s ORDER BY id",   # ONLY this user's, oldest first
            (user_id,),
        )
        rows = cursor.fetchall()
    messages = []
    for role, content, created_at in rows:        # each row is a tuple → unpack it 
        messages.append({"role": role, "content": content, "created_at": created_at})
    return messages

if __name__ == "__main__":
    create_tables()
    print("Tables are ready.") 