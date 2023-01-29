# pylint: disable=too-many-instance-attributes


from dataclasses import dataclass


@dataclass
class Config:
    """
    Configuration data class.
    """

    base_url: str
    database_url: str
    document_number: str
    vehicle_number: str
    anti_captcha_key: str

    smtp_server: str
    smtp_port: int
    smtp_username: str
    smtp_password: str

    notification_sender_email: str
    notification_receiver_email: str

    sms_notification_api_url: str
    sms_notification_username: str
    sms_notification_password: str
    sms_notification_receiver: str

    anti_captcha_soft_id: int = 0
    session_id: str = None
