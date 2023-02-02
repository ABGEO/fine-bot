import logging
import smtplib
import ssl
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import requests
from jinja2 import Environment, FileSystemLoader, select_autoescape

from config import Config


class Notifier:
    """
    Class for sending Email and SMS notifications.
    """

    def __init__(self):
        self._logger = logging.getLogger(__name__)
        self._config = Config()
        self._jinja_env = Environment(
            loader=FileSystemLoader("./templates"), autoescape=select_autoescape()
        )

    def notify_about_new_protocol(self, protocol):
        """
        Send notification about receiving new protocol.
        """

        self._logger.info(
            "Sending notifications about new protocol. Protocol #%s",
            protocol.protocol_number,
        )

        template_params = {
            "car_state_number": protocol.car_state_number,
            "violation_code": protocol.violation_code,
            "protocol_number": protocol.protocol_number,
            "date": protocol.date.strftime("%d/%m/%Y"),
            "amount": protocol.amount / 100,
        }

        self._send_email_and_sms(
            "new_protocol",
            template_params,
            "თქვენი სატრანსპორტო საშუალება დაჯარიმდა",
            list(map(lambda x: {"ext": x.type.value, "blob": x.blob}, protocol.media)),
        )

    def notify_about_successful_payment(self, protocol):
        """
        Send notification about successful payment.
        """

        self._logger.info(
            "Sending notifications about successful payment. Protocol #%s",
            protocol.protocol_number,
        )

        self._send_email_and_sms(
            "successful_payment",
            {"protocol_number": protocol.protocol_number},
            "ჯარიმის დაფარვა",
        )

    def _send_email_and_sms(
        self,
        template_name: str,
        template_params,
        email_subject: str,
        email_attachments: list = None,
    ):
        email_template = self._jinja_env.get_template(f"email/{template_name}.jinja2")
        sms_template = self._jinja_env.get_template(f"sms/{template_name}.jinja2")

        email_rendered = email_template.render(**template_params)
        sms_rendered = sms_template.render(**template_params)

        self._send_email(email_subject, email_rendered, email_attachments)
        self._send_sms_notification(sms_rendered)

    def _send_email(self, subject: str, html: str, attachments: list = None):
        message = MIMEMultipart()
        message["From"] = self._config.notification_sender_email
        message["To"] = self._config.notification_receiver_email
        message["Subject"] = subject

        message.attach(MIMEText(html, "html"))

        if attachments:
            for idx, attachment in enumerate(attachments):
                part = MIMEBase("application", "octet-stream")
                part.set_payload(attachment["blob"])
                encoders.encode_base64(part)
                part.add_header(
                    "Content-Disposition",
                    f"attachment; filename={idx+1}.{attachment['ext']}",
                )
                message.attach(part)

        with smtplib.SMTP_SSL(
            self._config.smtp_server,
            self._config.smtp_port,
            context=ssl.create_default_context(),
        ) as server:
            server.login(self._config.smtp_username, self._config.smtp_password)
            server.sendmail(
                self._config.notification_sender_email,
                self._config.notification_receiver_email,
                message.as_string(),
            )

            self._logger.info(
                "Email have been sent to %s", self._config.notification_receiver_email
            )

    def _send_sms_notification(self, text: str):
        response = requests.post(
            f"{self._config.sms_notification_api_url}/token",
            data={
                "grant_type": "password",
                "username": self._config.sms_notification_username,
                "password": self._config.sms_notification_password,
            },
            timeout=10,
        )
        data = response.json()

        requests.post(
            f"{self._config.sms_notification_api_url}/sms",
            json={
                "recipient": self._config.sms_notification_receiver,
                "message": text,
            },
            headers={"Authorization": f"Bearer {data['access_token']}"},
            timeout=10,
        )

        self._logger.info(
            "SMS have been sent to %s", self._config.sms_notification_receiver
        )
