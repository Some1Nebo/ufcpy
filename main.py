import logging

from crawler.parser import parse_fighter_page, parse_event_page
from storage import init_db
from storage.models.event import Event
from storage.models.fight import Fight
from storage.models.fighter import Fighter

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

if __name__ == "__main__":

    mysql_connection_string = "mysql+pymysql://{username}:{password}@{host}/{dbname}".format(
            username='tempuser',
            password='temppassword',
            host='localhost',
            dbname='ufcdb')

    memory_connection_string = 'sqlite:///:memory:'

    Session = init_db(mysql_connection_string, create=True)

    session = Session()

    parse_queue = ["/fighter/Jon-Jones-27944"]
    parsed = set()

    while len(parse_queue) != 0:
        logger.info("queue: {}, parsed: {}".format(len(parse_queue), len(parsed)))
        ref = parse_queue.pop(0)
        if ref in parsed:
            continue
        parsed.add(ref)

        logger.info("parsing {}".format(ref))

        try:
            fighter, fight_infos = parse_fighter_page(ref)
            if fighter.weight == 0 or fighter.height == 0:
                logger.warn("No midgets, {} skipped".format(fighter.name))
                continue

            fighter_in_db = session.query(Fighter).filter_by(ref=fighter.ref).first()

            if fighter_in_db:
                fighter = fighter_in_db
            else:
                session.add(fighter)

            for fight_info in fight_infos:
                fighter2 = session.query(Fighter).filter_by(ref=fight_info.fighter2_ref).first()

                if fighter2:
                    event = session.query(Event).filter_by(ref=fight_info.event_ref).first()

                    if not event:
                        event = parse_event_page(fight_info.event_ref)
                        session.add(event)

                    already_seen = filter(
                            lambda f: f.event == event and (f.fighter1 == fighter2 or f.fighter2 == fighter2),
                            fighter.fights)

                    if not already_seen:
                        logger.info("Creating a fight with fighter2 {}".format(fighter2.ref))
                        fight = Fight(fighter1=fighter,
                                      fighter2=fighter2,
                                      event=event,
                                      outcome=fight_info.outcome,
                                      method=fight_info.method,
                                      round=fight_info.round,
                                      time=fight_info.time)

                        session.add(fight)
                    else:
                        logger.info("Already seen {}, {}, {}".format(fighter.ref, fighter2.ref, event.ref))
                else:
                    parse_queue.append(fight_info.fighter2_ref)

        except Exception as e:
            logger.exception(e)

        session.commit()
