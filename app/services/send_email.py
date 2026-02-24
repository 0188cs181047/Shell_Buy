from fastapi_mail import FastMail, MessageSchema
from core.email import conf

async def send_register_email(email: str, username: str):
    subject = "Welcome to Our Platform"

    body = f"""
    <h2>Welcome {username},</h2>
    <p>Your account has been successfully created.</p>
    <p>We are happy to have you onboard.</p>
    """

    message = MessageSchema(
        subject=subject,
        recipients=[email],
        body=body,
        subtype="html"
    )

    fm = FastMail(conf)
    await fm.send_message(message)