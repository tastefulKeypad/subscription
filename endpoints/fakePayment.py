import random
import time

class FakePayment():
    def __init__(self, bankChange: int, status: str):
        self.bankChange = bankChange
        self.status = status

def fake_payment_method(
    price: int
) -> FakePayment:
    # Имитация сетевой задержки (реалистичное поведение)
    time.sleep(0.1)

    # Вероятности ошибок
    if random.random() < 0.05:  # 5% — таймаут (недоступность)
        return FakePayment(bankChange=0.0, status="Timeout")
    elif random.random() < 0.15:  # 15% — недостаток средств
        return FakePayment(bankChange=0.0, status="Insufficient funds")
    else:
        return FakePayment(bankChange=price, status="Success")


