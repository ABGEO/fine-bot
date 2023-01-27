from dataclasses import dataclass


@dataclass
class Config:
    base_url: str
    database_url: str
    anti_captcha_key: str
    document_number: str
    vehicle_number: str
    session_id: str = None
