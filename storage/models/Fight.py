from storage.models.base import *


class Fight(Base):
    __tablename__ = 'fights'

    id = Column(Integer, primary_key=True)
    fighter1_id = Column(Integer, ForeignKey('fighters.id'), nullable=False)
    fighter2_id = Column(Integer, ForeignKey('fighters.id'), nullable=False)
    event_id = Column(Integer, ForeignKey('events.id'))
    outcome = Column(Integer, nullable=False)
    method = Column(String)
    round = Column(Integer)
    time = Column(Time)

    fighter1 = relationship("Fighter", foreign_keys=[fighter1_id])
    fighter2 = relationship("Fighter", foreign_keys=[fighter2_id])
    event = relationship("Event", back_populates="fights")
