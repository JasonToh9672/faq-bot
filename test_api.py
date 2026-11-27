from datetime import datetime, timedelta, timezone

import jwt
import pytest
from fastapi.testclient import TestClient

from api import app
from auth import ALGORITHM, get_secret_key


@pytest.fixture
def client():                                     # a normal fixture: only tests that ask for "client" get it
    return TestClient(app)              


# it is normal function, not test function, the client we need to pass manually when calling signup_and_login because pytest only fills in fixtures for tests (and for other fixtures).
def signup_and_login(client, username, password="secret123"):    # a helper (not a test, not a fixture)
    client.post("/signup", json={"username": username, "password": password})
    response = client.post("/login", json={"username": username, "password": password})
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}                    # returns the ready-made HEADERS


def test_signup_works(client):
    response = client.post("/signup", json={"username": "toh", "password": "secret123"})
    assert response.status_code == 200
    assert response.json() == {"id": 1, "username": "toh"}        # id 1, thanks to RESTART IDENTITY


def test_signup_duplicate_returns_409(client):
    client.post("/signup", json={"username": "toh", "password": "secret123"})
    response = client.post("/signup", json={"username": "toh", "password": "another123"})
    assert response.status_code == 409


def test_login_wrong_password_returns_401(client):
    client.post("/signup", json={"username": "toh", "password": "secret123"})
    response = client.post("/login", json={"username": "toh", "password": "wrong-pass"})
    assert response.status_code == 401
    assert response.json() == {"detail": "Incorrect username or password"}


def test_me_with_token(client):
    headers = signup_and_login(client, "toh")
    response = client.get("/me", headers=headers)
    assert response.status_code == 200
    assert response.json() == {"id": 1, "username": "toh"}


def test_me_without_token_returns_401(client):
    response = client.get("/me")
    assert response.status_code == 401
    assert response.json() == {"detail": "Not authenticated"}      # from HTTPBearer (the first guard)


def test_me_with_fake_token_returns_401(client):
    response = client.get("/me", headers={"Authorization": "Bearer not-a-real-token"})
    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid or expired token"}   # from our guard (check 2)


def test_me_with_expired_token_returns_401(client):
    signup_and_login(client, "toh")                                    # user id 1 must exist
    expired = datetime.now(timezone.utc) - timedelta(minutes=1)
    token = jwt.encode({"sub": "1", "exp": expired}, get_secret_key(), algorithm=ALGORITHM)
    response = client.get("/me", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 401


def test_ask_saves_to_history(client):
    headers = signup_and_login(client, "toh")
    response = client.post("/ask", json={"question": "How do I get a refund?"}, headers=headers)
    assert response.status_code == 200
    history = client.get("/history", headers=headers).json()
    assert len(history) == 2                                           # the question + the answer
    assert history[0]["role"] == "user"
    assert history[0]["content"] == "How do I get a refund?"
    assert history[1]["role"] == "assistant"


def test_each_user_sees_only_their_own_history(client):               # THE "shared history" fix, proven
    toh_headers = signup_and_login(client, "toh")
    ali_headers = signup_and_login(client, "ali")
    client.post("/ask", json={"question": "refund?"}, headers=toh_headers)
    client.post("/ask", json={"question": "delivery?"}, headers=ali_headers)
    toh_history = client.get("/history", headers=toh_headers).json()
    ali_history = client.get("/history", headers=ali_headers).json()
    assert len(toh_history) == 2
    assert toh_history[0]["content"] == "refund?"
    assert len(ali_history) == 2
    assert ali_history[0]["content"] == "delivery?"


def test_new_user_has_empty_history(client):
    headers = signup_and_login(client, "toh")
    response = client.get("/history", headers=headers)
    assert response.json() == []


def test_ask_without_token_returns_401(client):
    response = client.post("/ask", json={"question": "refund?"})
    assert response.status_code == 401


def test_faq_is_public(client):
    response = client.get("/faq")
    assert response.status_code == 200
    assert "refund" in response.json()


def test_login_unknown_user_returns_401(client):
    response = client.post("/login", json={"username": "nobody", "password": "secret123"})
    assert response.status_code == 401
    assert response.json() == {"detail": "Incorrect username or password"}   # same message as a wrong password


def test_history_without_token_returns_401(client):
    response = client.get("/history")
    assert response.status_code == 401
    assert response.json() == {"detail": "Not authenticated"}                # from HTTPBearer (the first guard)