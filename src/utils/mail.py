from fastapi_mail import FastMail, ConnectionConfig, MessageType, MessageSchema

from src.config import Config

config = ConnectionConfig(
    MAIL_USERNAME="sunarsushil100@gmail.com",
    MAIL_PASSWORD=Config.MAIL_PASSWORD,
    MAIL_PORT=587,
    MAIL_SERVER="smtp.gmail.com",
    MAIL_FROM_NAME="Olofooto",
    MAIL_FROM="sunarsuhil100@gmail.com",
    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=False,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=False,
)
mail = FastMail(config)


async def send_mail(receiver_email: str, subject: str, body: str) -> None:
    try:
        await mail.send_message(
            message=MessageSchema(
                recipients=[receiver_email],
                body=body,
                subtype=MessageType.html,
                subject=subject,
            )
        )
    except Exception as e:
        print(f"Error while sending Mail: {e}")
        return None
