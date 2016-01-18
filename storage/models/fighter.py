from storage.models.base import *


class Fighter(Base):
    __tablename__ = 'fighters'

    id = Column(Integer, primary_key=True)
    ref = Column(String, unique=True, nullable=False)
    name = Column(String, nullable=False)
    city = Column(String)
    birthday = Column(Date)
    height = Column(Integer)    # centimeters
    weight = Column(Integer)    # kg
    record = Column(String)

    fights = relationship(
            "Fight",
            primaryjoin="or_(Fighter.id == Fight.first_fighter_id, Fighter.id == Fight.second_fighter_id)")
