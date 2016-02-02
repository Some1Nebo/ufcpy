from storage.models.base import *


class Fighter(Base):
    __tablename__ = 'fighters'

    id = Column(Integer, primary_key=True)
    ref = Column(String(STR_SIZE), unique=True, nullable=False)
    name = Column(String(STR_SIZE), nullable=False)
    country = Column(String(STR_SIZE))
    city = Column(String(STR_SIZE))
    birthday = Column(Date)
    height = Column(Integer)     # centimeters
    weight = Column(Integer)     # kg
    reach = Column(Integer)      # centimeters
    specialization = Column(String(STR_SIZE))

    fights = relationship(
            "Fight",
            primaryjoin="or_(Fighter.id == Fight.fighter1_id, Fighter.id == Fight.fighter2_id)")
