from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from storage.models.base import *

# create in-memory db
engine = create_engine('sqlite:///:memory:', echo=True)
Session = sessionmaker(bind=engine)


def init_db():
    print("Initializing storage. Creating all tables...")
    Base.metadata.create_all(engine)
