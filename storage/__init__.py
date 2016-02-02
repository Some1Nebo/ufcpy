from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from storage.models.base import *


def init_db(connection_string, create=False):
    engine = create_engine(connection_string, echo=True)
    if create:
        print("Initializing storage. Creating all tables...")
        Base.metadata.create_all(engine)
    return sessionmaker(bind=engine)
