from storage.models.base import *


class Fight(Base):
    __tablename__ = 'fights'

    id = Column(Integer, primary_key=True)
    first_fighter_id = Column(Integer, ForeignKey('fighters.id'), nullable=False)
    second_fighter_id = Column(Integer, ForeignKey('fighters.id'), nullable=False)
    outcome = Column(Integer, nullable=False)
    event_id = Column(Integer, ForeignKey('events.id'))
    method = Column(String)
    round = Column(Integer)
    time = Column(Time)

    first_fighter = relationship("Fighter", foreign_keys=[first_fighter_id])
    second_fighter = relationship("Fighter", foreign_keys=[second_fighter_id])
    event = relationship("Event", back_populates="fights")
