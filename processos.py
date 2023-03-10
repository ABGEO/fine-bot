import hashlib
import logging

from sqlalchemy import create_engine, select, Engine
from sqlalchemy.orm import Session

from config import Config
from key_value_storage import KeyValueStorage
from models import Base, Protocol
from scrapper import Scrapper


class Processor:
    """
    Main processor class for
    managing the scraping procedure.
    """

    def __init__(self):
        self._logger = logging.getLogger(__name__)
        self._config = Config()
        self._db_engine = self._setup_database()
        self._kvs = KeyValueStorage(self._db_engine)
        self._config.session_id = self._kvs.get(f"session_id_{self._session_id_key}")
        self._scrapper = Scrapper(self._config)

    def _setup_database(self) -> Engine:
        self._logger.debug("Setting up database")
        engine = create_engine(self._config.database_url, future=True)

        self._logger.debug("Applying database migrations")
        Base.metadata.create_all(engine)

        return engine

    @property
    def _session_id_key(self) -> str:
        result = hashlib.md5(
            bytes(
                f"{self._config.document_number}:{self._config.vehicle_number}".encode()
            )
        )
        return result.hexdigest()

    def process(self):
        """
        Start scrapping process and save results to database.
        """

        self._logger.debug(
            "Starting scrapping process for %s/%s",
            self._config.document_number,
            self._config.vehicle_number,
        )

        with Session(self._db_engine) as session:
            for protocol in self._scrapper.get_protocols():
                stmt = select(Protocol).where(
                    Protocol.protocol_number == protocol.protocol_number
                )
                loaded_protocol = session.scalars(stmt).first()

                if loaded_protocol is not None:
                    self._logger.info("Updating Protocol %s", protocol.protocol_number)
                    protocol.id = loaded_protocol.id
                    session.merge(protocol)
                else:
                    self._logger.info("Saving Protocol %s", protocol.protocol_number)
                    session.add(protocol)

            session.commit()

    def __del__(self):
        self._kvs.set(f"session_id_{self._session_id_key}", self._config.session_id)
