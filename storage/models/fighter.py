from storage.models.base import *
from sqlalchemy.orm import validates


class Fighter(Base):
    __tablename__ = 'fighters'

    id = Column(Integer, primary_key=True)
    ref = Column(String(STR_SIZE), unique=True, nullable=False)
    name = Column(String(STR_SIZE), nullable=False)
    country = Column(String(STR_SIZE))
    city = Column(String(STR_SIZE))
    birthday = Column(Date, nullable=False)
    height = Column(Integer)  # centimeters
    weight = Column(Float)  # kg
    reach = Column(Integer)  # centimeters
    specialization = Column(String(STR_SIZE))

    fights = relationship(
            "Fight",
            primaryjoin="or_(Fighter.id == Fight.fighter1_id, Fighter.id == Fight.fighter2_id)")

    @validates('height')
    def validate_height(self, key, height):
        assert height > 0
        return height

    @validates('weight')
    def validate_weight(self, key, weight):
        assert weight > 0
        return weight
