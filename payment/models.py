from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Enum
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
import enum

Base = declarative_base()

class PaymentStatus(str, enum.Enum):
    succeeded = "succeeded"
    insufficient_funds = "insufficient_funds"
    payment_method_expired = "payment_method_expired"
    declined = "declined"
    timeout = "timeout"
    processing = "processing"

class PaymentMethod(Base):
    __tablename__ = "payment_methods"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True)  # или Integer, если у тебя user_id = int
    token = Column(String, unique=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_successful_charge = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=True)

class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    external_id = Column(String, unique=True, index=True)  # idempotency key или наш ID
    user_id = Column(String, index=True)
    payment_method_token = Column(String)
    amount = Column(Float)
    currency = Column(String, default="RUB")
    status = Column(Enum(PaymentStatus))
    description = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)