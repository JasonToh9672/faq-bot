import os

import pytest
from dotenv import load_dotenv

load_dotenv()                                                 # read .env (for TEST_DATABASE_URL)

test_database_url = os.environ.get("TEST_DATABASE_URL")
if test_database_url is None:
    raise RuntimeError("TEST_DATABASE_URL is not set. Add it to .env (see .env.example).")
if "test" not in test_database_url:                           # safety guard
    raise RuntimeError("TEST_DATABASE_URL must point to a TEST database (its name must contain 'test').")
os.environ["DATABASE_URL"] = test_database_url                # from now on, db.py uses the TEST database

import db                                                     # must come AFTER the line above
# AFTER the switch: if db.py ever reads DATABASE_URL at import time, it still gets the TEST one

@pytest.fixture(autouse=True)                                 # autouse = run before EVERY test, without being asked, so each test gets a freshly wiped database
def clean_database():
    db.create_tables()                                        # make sure the tables exist (safe: IF NOT EXISTS)
    with db.get_connection() as connection:
        cursor = connection.cursor()
        cursor.execute("TRUNCATE users, messages RESTART IDENTITY CASCADE")   # empty both tables


# Any fixture written in conftest.py is shared with every test file in that folder (and its subfolders), without any import:
"""
Fixture written in...	Normal fixture (@pytest.fixture)	    Autouse fixture(@pytest.fixture(autouse=True))
conftest.py	            any test file can ask for it by name	runs before every test in every file
a test file	            only tests in that file can ask for it	runs only before tests in that file
"""