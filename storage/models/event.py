from storage.models.base import *


class Event(Base):
    __tablename__ = 'events'

    id = Column(Integer, primary_key=True)
    ref = Column(String(STR_SIZE), unique=True, nullable=False)
    name = Column(String(STR_SIZE), nullable=False)
    place = Column(String(STR_SIZE))
    date = Column(Date)

    fights = relationship("Fight", back_populates="event")
