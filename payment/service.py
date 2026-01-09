import uuid
import time
import random
from typing import Optional
from sqlalchemy.orm import Session
from .models import PaymentMethod, Transaction, PaymentStatus
from .exceptions import PaymentServiceUnavailable

class FakePaymentService:
    def __init__(self, db: Session, failure_rate: float = 0.1, timeout_rate: float = 0.05, delay: float = 0.1):
        self.db = db
        self.failure_rate = failure_rate      # вероятность отказа (нехватка средств и т.п.)
        self.timeout_rate = timeout_rate      # вероятность "недоступности"
        self.delay = delay                    # имитация задержки (в секундах)

    def _simulate_network(self):
        """Имитация задержки и недоступности"""
        if random.random() < self.timeout_rate:
            raise PaymentServiceUnavailable("Payment service is temporarily unavailable")
        time.sleep(self.delay)

    def save_payment_method(self, user_id: str) -> str:
        token = str(uuid.uuid4())
        method = PaymentMethod(user_id=user_id, token=token)
        self.db.add(method)
        self.db.commit()
        self.db.refresh(method)
        return token

    def get_payment_method(self, token: str) -> Optional[PaymentMethod]:
        return self.db.query(PaymentMethod).filter(PaymentMethod.token == token, PaymentMethod.is_active == True).first()

    def is_payment_method_valid(self, token: str) -> bool:
        method = self.get_payment_method(token)
        if not method:
            return False
        # Пример: токен "протухает", если не использовался 180 дней
        if method.last_successful_charge:
            from datetime import datetime, timedelta
            if datetime.utcnow() - method.last_successful_charge > timedelta(days=180):
                return False
        return True

    def charge(
        self,
        user_id: str,
        amount: float,
        token: str,
        description: str = "",
        idempotency_key: Optional[str] = None
    ) -> Transaction:
        # Проверка idempotency
        if idempotency_key:
            existing = self.db.query(Transaction).filter(Transaction.external_id == idempotency_key).first()
            if existing:
                return existing

        self._simulate_network()

        method = self.get_payment_method(token)
        if not method:
            status = PaymentStatus.declined
        elif not self.is_payment_method_valid(token):
            status = PaymentStatus.payment_method_expired
        elif random.random() < self.failure_rate:
            status = PaymentStatus.insufficient_funds
        else:
            status = PaymentStatus.succeeded
            # Обновляем last_successful_charge
            method.last_successful_charge = datetime.utcnow()
            self.db.add(method)

        tx = Transaction(
            external_id=idempotency_key or str(uuid.uuid4()),
            user_id=user_id,
            payment_method_token=token,
            amount=amount,
            description=description,
            status=status
        )
        self.db.add(tx)
        self.db.commit()
        self.db.refresh(tx)
        return tx

    def refund(self, transaction_id: int) -> bool:
        tx = self.db.query(Transaction).filter(Transaction.id == transaction_id).first()
        if not tx or tx.status != PaymentStatus.succeeded:
            return False
        # В реальности — вызов refund API; здесь просто отметим (опционально)
        refund_tx = Transaction(
            external_id=str(uuid.uuid4()),
            user_id=tx.user_id,
            payment_method_token=tx.payment_method_token,
            amount=-tx.amount,
            description=f"Refund for tx {tx.id}",
            status=PaymentStatus.succeeded
        )
        self.db.add(refund_tx)
        self.db.commit()
        return True