import logging
import smtplib
import ssl
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import requests

from config import Config
from models import Protocol

logger = logging.getLogger(__name__)


def send_notifications(protocol: Protocol, config: Config):
    """
    Send notifications about receiving new protocol.
    """

    _send_email_notification(protocol, config)
    _send_sms_notification(protocol, config)


def _send_email_notification(protocol: Protocol, config: Config):
    message = MIMEMultipart()
    message["From"] = config.notification_sender_email
    message["To"] = config.notification_receiver_email
    message["Subject"] = "თქვენი სატრანსპორტო საშუალება დაჯარიმდა"
    message.attach(MIMEText(_get_notification_message(protocol)))

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
        logger.info(
            "Sending Email notification for protocol %s", protocol.protocol_number
        )
        server.login(config.smtp_username, config.smtp_password)
        server.sendmail(
            config.notification_sender_email,
            config.notification_receiver_email,
            message.as_string(),
        )


def _get_notification_message(protocol: Protocol):
    return f"""თქვენი სატრანსპორტო საშუალება სახელმწიფო ნომრით: {protocol.car_state_number},
დაჯარიმდა {protocol.violation_code}თ.

ქვითრის ნომერი: {protocol.protocol_number}
თარიღი: {protocol.date}
თანხა: {protocol.amount/100} ლარი
"""


def _send_sms_notification(protocol: Protocol, config: Config):
    logger.info("Sending SMS notification for protocol %s", protocol.protocol_number)

    response = requests.post(
        f"{config.sms_notification_api_url}/token",
        data={
            "grant_type": "password",
            "username": config.sms_notification_username,
            "password": config.sms_notification_password,
        },
        timeout=10,
    )
    data = response.json()

    requests.post(
        f"{config.sms_notification_api_url}/sms",
        json={
            "recipient": config.sms_notification_receiver,
            "message": _get_notification_message(protocol),
        },
        headers={"Authorization": f"Bearer {data['access_token']}"},
        timeout=10,
    )
