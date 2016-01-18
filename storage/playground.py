from storage.models.fight import Fight
from storage.models.fighter import Fighter

from storage import Session, init_db
from storage.models.event import Event

if __name__ == "__main__":
    init_db()
    session = Session()

    tagir = Fighter(name='Tagir', ref='/fighter/tagir-1001')
    session.add(tagir)

    sergey = Fighter(name='Sergey', ref='/fighter/sergey-1002')
    session.add(sergey)

    ufc01 = Event(name='UFC 01', ref='/event/ufc-01')
    session.add(ufc01)

    f1 = Fight(fighter1=tagir, fighter2=sergey, event=ufc01, outcome='Tagir crushed him')
    session.add(f1)

    # e1 = session.query(Event).filter_by(name='UFC 01').first()
    # print(e1.fights[0].first_fighter.name)

    #t = session.query(Fighter).filter_by(name='Tagir').first()
    session.commit()

    t = session.query(Fight).first()

    tagir.name = "TTT"

    print(t.fighter1.name)
