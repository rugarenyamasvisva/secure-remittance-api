import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_register_user():
    response = client.post("/users", json={
        "name": "Tendai",
        "email": "tendai.test@example.com",
        "password": "Password123"
    })
    assert response.status_code in [201, 409]  # 201 created or 409 if already exists

def test_get_wallet():
    response = client.get("/wallets/1")
    assert response.status_code == 200
    data = response.json()
    assert "balance_cents" in data

def test_deposit():
    response = client.post("/wallets/1/deposit", json={
        "amount_cents": 50000
    })
    assert response.status_code in [200, 201]

def test_insufficient_funds_transfer():
    response = client.post("/transfers", json={
        "from_wallet_id": 1,
        "to_wallet_id": 2,
        "amount_cents": 9999999
    })
    assert response.status_code in [400, 422]