from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

MAX_AMOUNT_CENTS = 1_000_000  # 10,000.00 per operation
EMAIL_PATTERN = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"


class UserCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    email: str = Field(pattern=EMAIL_PATTERN, max_length=255)
    password: str = Field(min_length=8, max_length=128)


class UserOut(BaseModel):
    id: int
    name: str
    email: str
    wallet_id: int


class WalletOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    balance_cents: int


class DepositIn(BaseModel):
    amount_cents: int = Field(gt=0, le=MAX_AMOUNT_CENTS)


class TransferIn(BaseModel):
    from_wallet_id: int
    to_wallet_id: int
    amount_cents: int = Field(gt=0, le=MAX_AMOUNT_CENTS)


class TransactionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    sender_wallet_id: int | None
    receiver_wallet_id: int
    amount_cents: int
    kind: str
    status: str
    created_at: datetime
