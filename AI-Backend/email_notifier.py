import os
import smtplib
from email.message import EmailMessage


SMTP_HOST = os.getenv(
    "SMTP_HOST",
    "smtp.gmail.com"
)

SMTP_PORT = int(
    os.getenv(
        "SMTP_PORT",
        "587"
    )
)

SMTP_USERNAME = os.getenv(
    "SMTP_USERNAME"
)

SMTP_APP_PASSWORD = os.getenv(
    "SMTP_APP_PASSWORD"
)

SMTP_FROM = os.getenv(
    "SMTP_FROM",
    SMTP_USERNAME
)

SMTP_USE_AUTH = os.getenv(
    "SMTP_USE_AUTH",
    "true"
).lower() in (
    "1",
    "true",
    "yes",
    "on"
)


def send_email(
    recipient,
    subject,
    body
):
    """
    Send a plain-text Network Sentinel notification email.
    """

    if not SMTP_FROM:
        raise RuntimeError(
            "SMTP_FROM is required"
        )

    if not recipient:
        raise ValueError(
            "A notification recipient is required"
        )

    if SMTP_USE_AUTH:
        if not SMTP_USERNAME:
            raise RuntimeError(
                "SMTP_USERNAME is required when SMTP authentication is enabled"
            )

        if not SMTP_APP_PASSWORD:
            raise RuntimeError(
                "SMTP_APP_PASSWORD is required when SMTP authentication is enabled"
            )

    message = EmailMessage()

    message["Subject"] = subject
    message["From"] = SMTP_FROM
    message["To"] = recipient

    message.set_content(
        body
    )

    with smtplib.SMTP(
        SMTP_HOST,
        SMTP_PORT,
        timeout=30
    ) as server:

        server.ehlo()

        server.starttls()

        server.ehlo()

        if SMTP_USE_AUTH:
            server.login(
                SMTP_USERNAME,
                SMTP_APP_PASSWORD
            )

        server.send_message(
            message
        )

    return True