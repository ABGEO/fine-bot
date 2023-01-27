# pylint: disable=too-few-public-methods,missing-class-docstring

import datetime
import enum

from sqlalchemy import LargeBinary, ForeignKey
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import Date
from sqlalchemy import Enum
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship


class Base(DeclarativeBase):
    pass


class ProtocolStatus(enum.Enum):
    PAID_ON_TIME = 1
    UNPAID = 2


class Protocol(Base):
    __tablename__ = "protocol"

    id: Mapped[int] = mapped_column(primary_key=True)
    protocol_number: Mapped[str] = mapped_column(String(30), unique=True)
    car_state_number: Mapped[str] = mapped_column(String(10))
    date: Mapped[datetime.date] = mapped_column(Date)
    violation_code: Mapped[str] = mapped_column(String)
    amount: Mapped[int] = mapped_column(Integer)
    total_amount: Mapped[int] = mapped_column(Integer)
    status: Mapped[ProtocolStatus] = mapped_column(Enum(ProtocolStatus))
    media: Mapped[list["Media"]] = relationship(
        back_populates="protocol", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return (
            f"Protocol("
            f"id={self.id!r}, "
            f"protocol_number={self.protocol_number!r}, "
            f"car_state_number={self.car_state_number!r}, "
            f"date={self.date!r}, "
            f"violation_code={self.violation_code!r}, "
            f"amount={self.amount!r}, "
            f"total_amount={self.total_amount!r}, "
            f"status={self.status!r}, "
            f"media={self.media!r}"
            f")"
        )


class Media(Base):
    __tablename__ = "media"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    blob: Mapped[bin] = mapped_column(LargeBinary)
    protocol_id: Mapped[int] = mapped_column(ForeignKey("protocol.id"))
    protocol: Mapped["Protocol"] = relationship(back_populates="media")

    def __repr__(self):
        return f"Media(id={self.id!r}, protocol_id={self.protocol_id!r})"


class KeyValue(Base):
    __tablename__ = "key_value"

    key: Mapped[str] = mapped_column(String, primary_key=True)
    value: Mapped[str] = mapped_column(String)

    def __repr__(self):
        return f"KeyValue(key={self.key!r}, value={self.value!r})"