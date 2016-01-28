from crawler.sherdog_parser import parse_fighter_page

from storage.models.fight import Fight
from storage.models.fighter import Fighter

from storage import Session, init_db
from storage.models.event import Event


if __name__ == "__main__":

    init_db()
    session = Session()

    parse_queue = ["/fighter/Jon-Jones-27944"]
    parsed = set()

    while len(parse_queue) != 0:
        print("queue: {}, parsed: {}".format(len(parse_queue), len(parsed)))
        ref = parse_queue.pop(0)
        if ref in parsed:
            continue
        parsed.add(ref)

        print("parsing {}".format(ref))

        try:
            fighter, fight_infos = parse_fighter_page(ref)
            session.add(fighter)

            for fight_info in fight_infos:
                fighter2 = session.query(Fighter).filter_by(ref=fight_info.fighter2_ref).first()
                if fighter2:
                    fight = Fight(fighter1=fighter,
                                  fighter2=fighter2,
                                  event=None,
                                  outcome=fight_info.outcome,
                                  method=fight_info.method,
                                  round=fight_info.round,
                                  time=fight_info.time)

                    print("Creating a fight with fighter2 {}".format(fighter2.ref))
                    session.add(fight)
                else:
                    parse_queue.append(fight_info.fighter2_ref)

        except ValueError as e:
            print("Error parsing fighter {}, details: {}".format(ref, e))

        session.commit()
