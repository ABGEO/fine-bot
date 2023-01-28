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
    anti_captcha_soft_id: int = 0
    session_id: str = None
