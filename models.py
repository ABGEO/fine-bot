# pylint: disable=too-few-public-methods,missing-class-docstring,missing-function-docstring,unused-argument

import datetime
import enum

from sqlalchemy import LargeBinary, ForeignKey, event, Connection
from sqlalchemy import String
from sqlalchemy.orm import DeclarativeBase, Mapper, AttributeEventToken
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship

from notifier import Notifier

notifier = Notifier()


class Base(DeclarativeBase):
    pass


class ProtocolStatus(enum.Enum):
    PAID_ON_TIME = 1
    UNPAID = 2
    UNKNOWN = 2


class MediaType(enum.Enum):
    PNG = "png"
    OGG = "ogv"


class Protocol(Base):
    __tablename__ = "protocol"

    id: Mapped[int] = mapped_column(primary_key=True)
    protocol_number: Mapped[str] = mapped_column(String(30), unique=True)
    car_state_number: Mapped[str] = mapped_column(String(10))
    date: Mapped[datetime.date]
    violation_code: Mapped[str]
    amount: Mapped[int]
    status: Mapped[ProtocolStatus]
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
            f"status={self.status!r}, "
            f"media={self.media!r}"
            f")"
        )


class Media(Base):
    __tablename__ = "media"

    id: Mapped[int] = mapped_column(primary_key=True)
    blob: Mapped[bin] = mapped_column(LargeBinary)
    type: Mapped[MediaType]
    protocol_id: Mapped[int] = mapped_column(ForeignKey("protocol.id"))
    protocol: Mapped["Protocol"] = relationship(back_populates="media")

    def __repr__(self):
        return f"Media(id={self.id!r}, type={self.type!r}, protocol_id={self.protocol_id!r})"


class KeyValue(Base):
    __tablename__ = "key_value"

    key: Mapped[str] = mapped_column(primary_key=True)
    value: Mapped[str | None]

    def __repr__(self):
        return f"KeyValue(key={self.key!r}, value={self.value!r})"


@event.listens_for(Protocol, "after_insert")
def protocol_after_insert(mapper: Mapper, connection: Connection, target: Protocol):
    notifier.notify_about_new_protocol(target)


@event.listens_for(Protocol.status, "set")
def protocol_status_update(
    target: Protocol,
    value: ProtocolStatus,
    old_value: ProtocolStatus,
    initiator: AttributeEventToken,
):
    if target.id is None:
        return

    if value == old_value:
        return

    if value == ProtocolStatus.PAID_ON_TIME:
        notifier.notify_about_successful_payment(target)
