from sqlalchemy import Engine
from sqlalchemy.orm import Session
from models import KeyValue as KeyValueModel


class KeyValueStorage:
    """
    Key-Value storage.
    Stores setting in KeyValue model.
    """

    def __init__(self, engine: Engine):
        self._engine = engine

    def set(self, key: str, value: str):
        """
        Save key-value pair to the database.
        """

        with Session(self._engine) as session:
            entry = session.get(KeyValueModel, key)
            if entry:
                entry.value = value
            else:
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
                session.delete(entry)
                session.commit()
