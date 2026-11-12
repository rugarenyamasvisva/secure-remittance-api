# Secure Remittance API

A small backend for digital wallets, built with Python and FastAPI. Users can register, deposit money, send money to each other and see their transaction history. It is a learning and portfolio project, not a production system.

## What it does

- Registers users with salted password hashing, one wallet each
- Stores money as whole cents to avoid rounding errors
- Supports deposits and wallet-to-wallet transfers
- Transfers are all-or-nothing: if any step fails, nothing changes
- Rejects bad input: negative amounts, unknown wallets, duplicate emails and transfers to the same wallet
- Keeps a transaction history for every wallet

## Tech stack

Python, FastAPI, SQLAlchemy, SQLite, pytest

## Endpoints

| Method | Path | Purpose |
|--------|------|---------|
| POST | /users | Register a user and create their wallet |
| GET | /wallets/{id} | Get a wallet balance |
| POST | /wallets/{id}/deposit | Add money to a wallet |
| POST | /transfers | Send money between two wallets |
| GET | /wallets/{id}/transactions | List a wallet's transactions |

Amounts are in cents, so 10000 means 100.00.

## Run it

Open a terminal in the remittance-api folder, then run:

    python -m venv venv
    venv\Scripts\activate
    pip install -r requirements.txt
    uvicorn main:app --reload

Then open http://127.0.0.1:8000/docs to try the endpoints.

## Limitations

- No login yet, so any caller can use any wallet
- A repeated request creates a repeated transfer
- SQLite is used for simplicity; a real service would use PostgreSQL

## Author

Rugare Nyamasvisva, Harare, Zimbabwe
