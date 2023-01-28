import logging

from sqlalchemy import Engine
from sqlalchemy.orm import Session
from models import KeyValue as KeyValueModel


class KeyValueStorage:
    """
    Key-Value storage.
    Stores setting in KeyValue model.
    """

    def __init__(self, engine: Engine):
        self._logger = logging.getLogger(__name__)
        self._engine = engine

    def set(self, key: str, value: str):
        """
        Save key-value pair to the database.
        """

        with Session(self._engine) as session:
            entry = session.get(KeyValueModel, key)
            if entry:
                self._logger.debug("Updating key-value pair: %s=%s", key, value)
                entry.value = value
            else:
                self._logger.debug("Creating key-value pair: %s=%s", key, value)
                settings = KeyValueModel(key=key, value=value)
                session.add(settings)

            session.commit()

    def get(self, key: str, default=None):
        """
        Get value by key from the database.
        """

        with Session(self._engine) as session:
            entry = session.get(KeyValueModel, key)
            return entry.value if entry is not None else default

    def delete(self, key: str):
        """
        Remove key-value pair..
        """

        with Session(self._engine) as session:
            entry = session.get(KeyValueModel, key)
            if entry:
                self._logger.debug("Deleting key-value pair with key %s", key)
                session.delete(entry)
                session.commit()
