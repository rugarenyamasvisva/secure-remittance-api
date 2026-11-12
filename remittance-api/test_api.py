import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from database import Base, get_db
from main import app


@pytest.fixture()
def client():
    """Each test gets a fresh, empty in-memory database."""
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSession = sessionmaker(bind=engine, autoflush=False)
    Base.metadata.create_all(bind=engine)

    def override_get_db():
        db = TestingSession()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


def make_user(client, name, email):
    """Registers a user and returns their wallet id."""
    response = client.post(
        "/users", json={"name": name, "email": email, "password": "Password123"}
    )
    assert response.status_code == 201
    return response.json()["wallet_id"]


def balance(client, wallet_id):
    return client.get(f"/wallets/{wallet_id}").json()["balance_cents"]


def test_register_creates_wallet_with_zero_balance(client):
    wallet_id = make_user(client, "Tendai", "tendai@example.com")
    assert balance(client, wallet_id) == 0


def test_duplicate_email_is_rejected(client):
    make_user(client, "Tendai", "tendai@example.com")
    response = client.post(
        "/users",
        json={"name": "Other", "email": "tendai@example.com", "password": "Password123"},
    )
    assert response.status_code == 409


def test_short_password_is_rejected(client):
    response = client.post(
        "/users",
        json={"name": "Tendai", "email": "t@example.com", "password": "short"},
    )
    assert response.status_code == 422


def test_deposit_increases_balance(client):
    wallet_id = make_user(client, "Tendai", "tendai@example.com")
    response = client.post(f"/wallets/{wallet_id}/deposit", json={"amount_cents": 5000})
    assert response.status_code == 201
    assert balance(client, wallet_id) == 5000


def test_successful_transfer_moves_money(client):
    a = make_user(client, "Tendai", "tendai@example.com")
    b = make_user(client, "Rudo", "rudo@example.com")
    client.post(f"/wallets/{a}/deposit", json={"amount_cents": 50000})

    response = client.post(
        "/transfers",
        json={"from_wallet_id": a, "to_wallet_id": b, "amount_cents": 10000},
    )
    assert response.status_code == 201
    assert balance(client, a) == 40000
    assert balance(client, b) == 10000


def test_insufficient_funds_changes_nothing(client):
    a = make_user(client, "Tendai", "tendai@example.com")
    b = make_user(client, "Rudo", "rudo@example.com")
    client.post(f"/wallets/{a}/deposit", json={"amount_cents": 1000})

    response = client.post(
        "/transfers",
        json={"from_wallet_id": a, "to_wallet_id": b, "amount_cents": 5000},
    )
    assert response.status_code == 400
    assert balance(client, a) == 1000
    assert balance(client, b) == 0


def test_negative_amount_is_rejected(client):
    wallet_id = make_user(client, "Tendai", "tendai@example.com")
    response = client.post(f"/wallets/{wallet_id}/deposit", json={"amount_cents": -5})
    assert response.status_code == 422


def test_transfer_to_same_wallet_is_rejected(client):
    a = make_user(client, "Tendai", "tendai@example.com")
    client.post(f"/wallets/{a}/deposit", json={"amount_cents": 1000})
    response = client.post(
        "/transfers",
        json={"from_wallet_id": a, "to_wallet_id": a, "amount_cents": 100},
    )
    assert response.status_code == 400


def test_unknown_wallet_returns_404(client):
    assert client.get("/wallets/99").status_code == 404
    response = client.post("/wallets/99/deposit", json={"amount_cents": 100})
    assert response.status_code == 404


def test_history_lists_deposit_and_transfer(client):
    a = make_user(client, "Tendai", "tendai@example.com")
    b = make_user(client, "Rudo", "rudo@example.com")
    client.post(f"/wallets/{a}/deposit", json={"amount_cents": 5000})
    client.post(
        "/transfers",
        json={"from_wallet_id": a, "to_wallet_id": b, "amount_cents": 1000},
    )
    history = client.get(f"/wallets/{a}/transactions").json()
    assert [t["kind"] for t in history] == ["transfer", "deposit"]
