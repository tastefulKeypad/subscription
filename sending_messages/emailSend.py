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