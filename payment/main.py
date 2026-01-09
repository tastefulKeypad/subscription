from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from payment.service import FakePaymentService
from payment.exceptions import PaymentServiceUnavailable

app = FastAPI()

def get_payment_service(db: Session = Depends(get_db)) -> FakePaymentService:
    return FakePaymentService(db, failure_rate=0.1, timeout_rate=0.05, delay=0.05)

@app.post("/payment-methods/")
def create_payment_method(user_id: str, payment_service: FakePaymentService = Depends(get_payment_service)):
    token = payment_service.save_payment_method(user_id)
    return {"token": token}

@app.post("/charge/")
def charge(
    user_id: str,
    amount: float,
    token: str,
    description: str = "",
    idempotency_key: str = None,
    payment_service: FakePaymentService = Depends(get_payment_service)
):
    try:
        tx = payment_service.charge(user_id, amount, token, description, idempotency_key)
        return {
            "transaction_id": tx.id,
            "status": tx.status,
            "amount": tx.amount
        }
    except PaymentServiceUnavailable:
        raise HTTPException(status_code=503, detail="Payment service is temporarily unavailable")