import hashlib
import os

from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy import or_, select
from sqlalchemy.orm import Session

import models
from database import Base, engine, get_db
from schemas import (
    DepositIn,
    TransactionOut,
    TransferIn,
    UserCreate,
    UserOut,
    WalletOut,
)

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Secure Remittance API", version="1.0")


def hash_password(password: str) -> str:
    """Salted PBKDF2 hash. The plain password is never stored."""
    salt = os.urandom(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 200_000)
    return f"{salt.hex()}:{digest.hex()}"


@app.post("/users", response_model=UserOut, status_code=201)
def register_user(data: UserCreate, db: Session = Depends(get_db)):
    existing = db.scalar(select(models.User).where(models.User.email == data.email))
    if existing:
        raise HTTPException(status_code=409, detail="Email already registered")

    user = models.User(
        name=data.name,
        email=data.email,
        password_hash=hash_password(data.password),
    )
    db.add(user)
    db.flush()  # assigns user.id without finishing the transaction
    wallet = models.Wallet(user_id=user.id, balance_cents=0)
    db.add(wallet)
    db.commit()
    return UserOut(id=user.id, name=user.name, email=user.email, wallet_id=wallet.id)


@app.get("/wallets/{wallet_id}", response_model=WalletOut)
def get_wallet(wallet_id: int, db: Session = Depends(get_db)):
    wallet = db.get(models.Wallet, wallet_id)
    if not wallet:
        raise HTTPException(status_code=404, detail="Wallet not found")
    return wallet


@app.post("/wallets/{wallet_id}/deposit", response_model=TransactionOut, status_code=201)
def deposit(wallet_id: int, data: DepositIn, db: Session = Depends(get_db)):
    wallet = db.get(models.Wallet, wallet_id)
    if not wallet:
        raise HTTPException(status_code=404, detail="Wallet not found")

    try:
        wallet.balance_cents += data.amount_cents
        tx = models.Transaction(
            sender_wallet_id=None,
            receiver_wallet_id=wallet.id,
            amount_cents=data.amount_cents,
            kind="deposit",
        )
        db.add(tx)
        db.commit()
    except Exception:
        db.rollback()
        raise HTTPException(status_code=500, detail="Deposit failed")
    db.refresh(tx)
    return tx


@app.post("/transfers", response_model=TransactionOut, status_code=201)
def transfer(data: TransferIn, db: Session = Depends(get_db)):
    if data.from_wallet_id == data.to_wallet_id:
        raise HTTPException(status_code=400, detail="Cannot transfer to the same wallet")

    sender = db.get(models.Wallet, data.from_wallet_id)
    receiver = db.get(models.Wallet, data.to_wallet_id)
    if not sender or not receiver:
        raise HTTPException(status_code=404, detail="Wallet not found")
    if sender.balance_cents < data.amount_cents:
        raise HTTPException(status_code=400, detail="Insufficient funds")

    # Both balance changes and the record are saved together or not at all.
    try:
        sender.balance_cents -= data.amount_cents
        receiver.balance_cents += data.amount_cents
        tx = models.Transaction(
            sender_wallet_id=sender.id,
            receiver_wallet_id=receiver.id,
            amount_cents=data.amount_cents,
            kind="transfer",
        )
        db.add(tx)
        db.commit()
    except Exception:
        db.rollback()
        raise HTTPException(status_code=500, detail="Transfer failed, nothing was changed")
    db.refresh(tx)
    return tx


@app.get("/wallets/{wallet_id}/transactions", response_model=list[TransactionOut])
def list_transactions(wallet_id: int, db: Session = Depends(get_db)):
    if not db.get(models.Wallet, wallet_id):
        raise HTTPException(status_code=404, detail="Wallet not found")
    stmt = (
        select(models.Transaction)
        .where(
            or_(
                models.Transaction.sender_wallet_id == wallet_id,
                models.Transaction.receiver_wallet_id == wallet_id,
            )
        )
        .order_by(models.Transaction.id.desc())
    )
    return list(db.scalars(stmt))
