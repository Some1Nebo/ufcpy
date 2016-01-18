from storage.models.base import *


class Event(Base):
    __tablename__ = 'events'

    id = Column(Integer, primary_key=True)
    ref = Column(String, unique=True, nullable=False)
    name = Column(String, nullable=False)
    place = Column(String)
    date = Column(Date)

    fights = relationship("Fight", back_populates="event")
