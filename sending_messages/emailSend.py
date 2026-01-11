import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from securityConfig import SMTP_SERVER, SMTP_PORT, SMTP_USERNAME, SMTP_PASSWORD


def send_email(mail: str, topic: str, body: str) -> bool:
    """
    Отправляет email через SMTP.
    """
    try:
        msg = MIMEMultipart()
        msg["From"] = SMTP_USERNAME
        msg["To"] = mail
        msg["Subject"] = topic
        msg.attach(MIMEText(body, "plain", "utf-8"))

        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USERNAME, SMTP_PASSWORD)
            server.send_message(msg)

        print(f"Email sent to {mail}: {topic}")
        return True

    except Exception as e:
        print(f"Failed to send email to {mail}: {e}")
        return False

def new_subscription(mail: str, productName: str, price: int):
    """
    Отправляет сообщение об успешной новой подписке
    """
    send_email(mail, f"Новая подписка на {productName}", f"Вы успешно оплатили {price} за оформление подписки на {productName}!")

def successfull_refund(mail: str, productName: str, price: int):
    """
    Отправляет сообщение об успешном возврате средств
    """
    send_email(mail, f"Возврат средств за {productName}", f"Мы вернули Вам {price} за {productName}!")

def payment_subscription(mail: str, productName: str, price: int):
    """
    Отправляет сообщение об успешной оплате существующей подписки
    """
    send_email(mail, f"Оплата подписки на {productName}", f"Автоматическое списание {price} за подписку на {productName}!")





