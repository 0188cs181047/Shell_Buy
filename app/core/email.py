import os
from fastapi_mail import ConnectionConfig

MAIL_USERNAME = os.getenv("MAIL_USERNAME", "acteviashiv@gmail.com")
MAIL_PASSWORD = os.getenv("MAIL_PASSWORD", "jblmpidoyeyupijp")
MAIL_FROM = os.getenv("MAIL_FROM", "acteviashiv@gmail.com")
MAIL_PORT = int(os.getenv("MAIL_PORT", 587))
MAIL_SERVER = os.getenv("MAIL_SERVER", "smtp.gmail.com")

conf = ConnectionConfig(
    MAIL_USERNAME=MAIL_USERNAME,
    MAIL_PASSWORD=MAIL_PASSWORD,
    MAIL_FROM=MAIL_FROM,
    MAIL_PORT=MAIL_PORT,
    MAIL_SERVER=MAIL_SERVER,
    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=False,
    USE_CREDENTIALS=True,
)