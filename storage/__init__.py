from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from storage.models.event import Event
from storage.models.base import *

import logging

logger = logging.getLogger(__name__)


def init_db(connection_string, create=False):
    engine = create_engine(connection_string, echo=False)
    if create:
        logger.info("Initializing storage. Creating all tables...")
        Base.metadata.create_all(engine)
    return sessionmaker(bind=engine)
