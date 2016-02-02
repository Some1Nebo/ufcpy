import urllib

from datetime import datetime
from BeautifulSoup import BeautifulSoup
from storage.models.fighter import Fighter
from crawler.fight_info import FightInfo
from storage.models.fight import Fight
from storage.models.event import Event


def parse_fighter_page(ref):

    parsed_html = _download_sherdog_page(ref)
    fighter = _parse_fighter(ref, parsed_html)
    fight_infos = _parse_fight_infos(ref, parsed_html)

    parsed_html = _download_ufc_page(fighter.name)
    reach, specialization = _parse_ufc_fighter_info(parsed_html)

    fighter.reach = reach
    fighter.specialization = specialization

    return fighter, fight_infos


def _parse_fighter(ref, parsed_html):

    name = parsed_html.body.find('span', attrs={'class': 'fn'}).text

    birthday_str = parsed_html.body.find('span', attrs={'itemprop': 'birthDate'}).text
    birthday = datetime.strptime(birthday_str, "%Y-%m-%d")

    city = parsed_html.body.find('span', attrs={'itemprop': 'addressLocality'}).text
    country = parsed_html.body.find('strong', attrs={'itemprop': 'nationality'}).text

    height_str = parsed_html.body.find('span', attrs={'class': 'item height'}).contents[-1]
    height = float(height_str.strip().split(' ')[0])

    weight_str = parsed_html.body.find('span', attrs={'class': 'item weight'}).contents[-1]
    weight = float(weight_str.strip().split(' ')[0])

    return Fighter(ref=ref, name=name, country=country, city=city, birthday=birthday, height=height,
                   weight=weight)

def _parse_ufc_fighter_info(parsed_html):
    reach_str = parsed_html.body.find('td', attrs={'id': 'fighter-reach'}).text.split('"')[0]
    specialization = parsed_html.body.find('td', attrs={'id': 'fighter-skill-summary'}).text

    reach = int(float(reach_str) * 2.54)

    return reach, specialization


def _parse_fight_infos(fighter_ref, parsed_html):
    history_tags = parsed_html.body.findAll('div', attrs={'class': 'module fight_history'})
    history_tag = filter(lambda tag: tag.findAll('h2', text='Fight History'), history_tags)[0]

    fight_infos = []
    fight_rows = history_tag.findAll('tr')[1:]

    for fight_row in fight_rows:
        tds = fight_row.findAll('td')
        fight_info = FightInfo(
            fighter1_ref=fighter_ref,
            fighter2_ref=tds[1].a['href'],
            event_ref=tds[2].a['href'],
            outcome=tds[0].span.text,
            method=tds[3].find(text=True, recursive=False),
            round=tds[4].text,
            time=datetime.strptime(tds[5].text, "%M:%S").time()
        )
        fight_infos.append(fight_info)

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

