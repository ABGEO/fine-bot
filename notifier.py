import logging
import smtplib
import ssl
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from config import Config
from models import Protocol

logger = logging.getLogger(__name__)


def send_email_notification(protocol: Protocol, config: Config):
    """
    Send email notification about receiving new protocol.
    """

    body = f"""
    თქვენი სატრანსპორტო საშუალება სახელმწიფო ნომრით: {protocol.car_state_number},
    დაჯარიმდა {protocol.violation_code}თ.

    ქვითრის ნომერი: {protocol.protocol_number}
    თარიღი: {protocol.date}
    თანხა: {protocol.amount/100} ლარი
    """

    message = MIMEMultipart()
    message["From"] = config.notification_sender_email
    message["To"] = config.notification_receiver_email
    message["Subject"] = "თქვენი სატრანსპორტო საშუალება დაჯარიმდა"
    message.attach(MIMEText(body))

    for idx, media in enumerate(protocol.media):
        part = MIMEBase("application", "octet-stream")
        part.set_payload(media.blob)
        encoders.encode_base64(part)
        part.add_header(
            "Content-Disposition",
            f"attachment; filename={idx+1}.{media.type.value}",
        )
        message.attach(part)

    with smtplib.SMTP_SSL(
        config.smtp_server, config.smtp_port, context=ssl.create_default_context()
    ) as server:
        server.login(config.smtp_username, config.smtp_password)
        server.sendmail(
            config.notification_sender_email,
            config.notification_receiver_email,
            message.as_string(),
        )
