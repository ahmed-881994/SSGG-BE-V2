from sqlalchemy.orm import DeclarativeBase

from app.core.database import engine


class Base(DeclarativeBase):
    def __init__(self):
        self.metadata.create_all(engine)