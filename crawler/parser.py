import logging
import urllib
from datetime import datetime

import dateutil.parser
from BeautifulSoup import BeautifulSoup

from crawler.fight_info import FightInfo
from storage.models.event import Event
from storage.models.fighter import Fighter

logger = logging.getLogger(__name__)


class FighterData:
    def __init__(self, sherdog_page, wiki_page, ufc_page):
        self.sherdog_page = sherdog_page
        self.wiki_page = wiki_page
        self.ufc_page = ufc_page

    def _extract(self, extractors, idx=0):
        if idx >= len(extractors):
            return None

        try:
            return extractors[idx](self)
        except:
            return self._extract(extractors, idx + 1)

    def extract(self, *extractors):
        return self._extract(extractors)


def parse_fighter_page(ref):
    # parse main info from Sherdog
    logger.info("Parsing Sherdog info for {}".format(ref))

    sherdog_page = _download_sherdog_page(ref)

    fighter_name = sherdog_page.body.find('span', attrs={'class': 'fn'}).text

    fighter_data = FighterData(
            sherdog_page,
            _download_wiki_page(fighter_name),
            _download_ufc_page(fighter_name)
    )

    # extract each field
    fighter = Fighter(ref=ref, name=fighter_name)
    fighter.country = fighter_data.extract(country_extractor)
    fighter.city = fighter_data.extract(city_extractor)
    fighter.birthday = fighter_data.extract(wiki_birthday_extractor, sherdog_birthday_extractor)
    fighter.height = fighter_data.extract(height_extractor)
    fighter.weight = fighter_data.extract(weight_extractor)
    fighter.reach = fighter_data.extract(wiki_reach_extractor, ufc_reach_extractor)
    fighter.specialization = fighter_data.extract(spec_extractor)

    fight_infos = _parse_fight_infos(ref, sherdog_page)
    return fighter, fight_infos


def country_extractor(fighter_data):
    return fighter_data.sherdog_page.body.find('strong', attrs={'itemprop': 'nationality'}).text


def city_extractor(fighter_data):
    return fighter_data.sherdog_page.body.find('span', attrs={'itemprop': 'addressLocality'}).text


def sherdog_birthday_extractor(fighter_data):
    birthday_str = fighter_data.sherdog_page.body.find('span', attrs={'itemprop': 'birthDate'}).text
    return datetime.strptime(birthday_str, "%Y-%m-%d")


def wiki_birthday_extractor(fighter_data):
    bday_text = fighter_data.wiki_page.body.find('span', attrs={'class': 'bday'}).text
    return dateutil.parser.parse(bday_text)


def height_extractor(fighter_data):
    height_str = fighter_data.sherdog_page.body.find('span', attrs={'class': 'item height'}).contents[-1]
    return float(height_str.strip().split(' ')[0])


def weight_extractor(fighter_data):
    weight_str = fighter_data.sherdog_page.body.find('span', attrs={'class': 'item weight'}).contents[-1]
    return float(weight_str.strip().split(' ')[0])


def ufc_reach_extractor(fighter_data):
    reach_str = fighter_data.ufc_page.body.find('td', attrs={'id': 'fighter-reach'}).text.split('"')[0]
    return int(float(reach_str) * 2.54)


def wiki_reach_extractor(fighter_data):
    th = fighter_data.wiki_page.body.find('th', text='Reach')
    td_text = th.findNext('td').text
    reach_str = td_text.split('(')[-1].split('&')[0]
    return int(reach_str)


def spec_extractor(fighter_data):
    return fighter_data.ufc_page.body.find('td', attrs={'id': 'fighter-skill-summary'}).text


def parse_event_page(ref):
    event_page = _download_sherdog_page(ref)

    name = event_page.body.find('span', attrs={'itemprop': 'name'}).text
    place = event_page.body.find('span', attrs={'itemprop': 'location'}).text
    date = dateutil.parser.parse(event_page.body.find('meta', attrs={'itemprop': 'startDate'})['content'])

    return Event(ref=ref,
                 name=name,
                 place=place,
                 date=date.date())


def _parse_fight_infos(fighter_ref, parsed_html):
    history_tags = parsed_html.body.findAll('div', attrs={'class': 'module fight_history'})
    history_tag = filter(lambda tag: tag.findAll('h2', text='Fight History'), history_tags)[0]

    fight_infos = []
    fight_rows = history_tag.findAll('tr')[1:]

    for fight_row in fight_rows:
        tds = fight_row.findAll('td')

        # minor workaround as precise time is not important if missing
        time = tds[5].text
        if time == "N/A":
            time = "1:30"

        # if fight fails to parse, skip it instead of failing the whole fighter
        try:
            fight_info = FightInfo(
                    fighter1_ref=fighter_ref,
                    fighter2_ref=tds[1].a['href'],
                    event_ref=tds[2].a['href'],
                    outcome=tds[0].span.text,
                    method=tds[3].find(text=True, recursive=False),
                    round=tds[4].text,
                    time=datetime.strptime(time, "%M:%S").time())
            fight_infos.append(fight_info)
        except ValueError as e:
            logger.warning("Failed to parse fight info for {fighter}, exception: {ex}, row: {row}. Skipping...".format(
                    fighter=fighter_ref,
                    ex=e,
                    row=str(tds)
            ))

    return fight_infos


def _download_sherdog_page(ref):
    url = "http://www.sherdog.com" + ref
    socket = urllib.urlopen(url)
    page = socket.read()
    socket.close()
    return BeautifulSoup(page)


def _download_ufc_page(fighter_name):
    url = "http://www.ufc.com/fighter/" + fighter_name.strip().replace(" ", "-")
    socket = urllib.urlopen(url)
    page = socket.read()
    socket.close()
    return BeautifulSoup(page)


def _download_wiki_page(fighter_name):
    url = "https://en.wikipedia.org/wiki/" + fighter_name.strip().replace(" ", "_")
    socket = urllib.urlopen(url)
    page = socket.read()
    socket.close()
    return BeautifulSoup(page)
