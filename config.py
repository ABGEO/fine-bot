# pylint: disable=too-many-instance-attributes
import os
from dataclasses import dataclass

from dotenv import load_dotenv, dotenv_values


@dataclass
class Config:
    """
    Configuration data class.
    """

    def __init__(self):
        load_dotenv()

        env = {
            **dotenv_values(".env.base"),
            **dotenv_values(".env.local"),
            **os.environ,
        }

        self.base_url: str = env.get("BASE_URL")
        self.database_url: str = env.get("DATABASE_URL")
        self.document_number: str = env.get("DOCUMENT_NUMBER")
        self.vehicle_number: str = env.get("VEHICLE_NUMBER")

        self.anti_captcha_key: str = env.get("ANTI_CAPTCHA_KEY")
        self.anti_captcha_soft_id: int = env.get("ANTI_CAPTCHA_SOFT_ID", 0)

        self.smtp_server: str = env.get("SMTP_SERVER")
        self.smtp_port: int = env.get("SMTP_PORT")
        self.smtp_username: str = env.get("SMTP_USERNAME")
        self.smtp_password: str = env.get("SMTP_PASSWORD")

        self.notification_sender_email: str = env.get("NOTIFICATION_SENDER_EMAIL")
        self.notification_receiver_email: str = env.get("NOTIFICATION_RECEIVER_EMAIL")

        self.sms_notification_api_url: str = env.get("SMS_NOTIFICATION_API_URL")
        self.sms_notification_username: str = env.get("SMS_NOTIFICATION_USERNAME")
        self.sms_notification_password: str = env.get("SMS_NOTIFICATION_PASSWORD")
        self.sms_notification_receiver: str = env.get("SMS_NOTIFICATION_RECEIVER")

        self.session_id: str | None = None
