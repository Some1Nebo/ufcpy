from storage.models.base import *


class Fighter(Base):
    __tablename__ = 'fighters'

    id = Column(Integer, primary_key=True)
    ref = Column(String, unique=True, nullable=False)
    name = Column(String, nullable=False)
    country = Column(String)
    city = Column(String)
    birthday = Column(DateTime)
    height = Column(Integer)    # centimeters
    weight = Column(Integer)    # kg

    fights = relationship(
            "Fight",
            primaryjoin="or_(Fighter.id == Fight.fighter1_id, Fighter.id == Fight.fighter2_id)")
