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


if __name__ == "__main__":
    create_tables()
    print("Tables are ready.") 