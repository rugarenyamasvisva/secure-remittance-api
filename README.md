# Secure Remittance API

A production-ready, lightweight remittance and wallet management API built with **FastAPI** in Python and thoroughly validated using automated tests with **Pytest**.

---

## 1. Project Overview & Features
This project provides a secure backend service to manage user balances, process deposits, and execute peer-to-peer monetary transfers.

- **Wallet Management (`POST /wallets`, `GET /wallets/{id}`):** Account creation and real-time balance retrieval.
- **Deposit Processing (`POST /wallets/{id}/deposit`):** Securely credits funds to specified user wallets.
- **Transfer Validation (`POST /transfers`):** Executes atomic peer-to-peer fund transfers while handling edge cases like insufficient funds.

---

## 2. Tech Stack
- **Framework:** FastAPI (Python 3.12)
- **ASGI Server:** Uvicorn
- **Testing Suite:** Pytest & HTTPX
- **Version Control:** Git & GitHub

---

## 3. How It Works Under the Hood

### API Routing & Schema Validation (FastAPI)
FastAPI receives incoming HTTP JSON requests, parses inputs into Python data types, runs validation, and routes requests directly to core business logic handlers.

### Automated Test Execution (Pytest)
`pytest` simulates incoming HTTP client requests against the API endpoints. It validates HTTP status codes (`200 OK`, `201 Created`) and verifies JSON payload schemas without needing to manually spin up an external web browser.

---

## 4. Test Suite Execution Results

All core endpoints pass automated verification checks:

```text
============================== test session starts ==============================
platform win32 -- Python 3.12.10, pytest-9.2.0, pluggy-1.7.0
rootdir: C:\Users\Dell PC\Documents\remittance-api-day1
plugins: anyio-4.16.0
collected 4 items

remittance-api/test_api.py ....                                          [100%]

=============================== 4 passed in 1.92s ===============================