import time
import urllib

from BeautifulSoup import BeautifulSoup
from storage.models.fighter import Fighter
from storage.models.fight import Fight
from storage.models.event import Event

from crawler.fighter_record import FighterRecord


def parse_fighter_page(url):
    socket = urllib.urlopen(url)
    page = socket.read()
    parsed_html = BeautifulSoup(page)

    fighter = _parse_fighter(url, parsed_html)
    _parse_opponents(parsed_html)

    print(fighter.record)
    socket.close()

    return fighter


def _parse_fighter(url, parsed_html):
    ref = url.split('/')[-1]

    name = parsed_html.body.find('span', attrs={'class': 'fn'}).text

    birthday_str = parsed_html.body.find('span', attrs={'itemprop': 'birthDate'}).text
    birthday = time.strptime(birthday_str, "%Y-%m-%d")

    city = parsed_html.body.find('span', attrs={'itemprop': 'addressLocality'}).text
    country = parsed_html.body.find('strong', attrs={'itemprop': 'nationality'}).text

    height_str = parsed_html.body.find('span', attrs={'class': 'item height'}).contents[-1]
    height = float(height_str.strip().split(' ')[0])

    weight_str = parsed_html.body.find('span', attrs={'class': 'item weight'}).contents[-1]
    weight = float(weight_str.strip().split(' ')[0])

    w_section = parsed_html.body.find('div', attrs={'class': 'bio_graph'})
    w_outcomes = w_section.findAll('span', attrs={'class': 'graph_tag'})
    w_ko_str = w_outcomes[0].text.split('KO/TKO')[0]
    w_submission_str = w_outcomes[1].text.split('SUBMISSIONS')[0]
    w_decision_str = w_outcomes[2].text.split('DECISIONS')[0]

    l_section = parsed_html.body.find('div', attrs={'class': 'bio_graph loser'})
    l_outcomes = l_section.findAll('span', attrs={'class': 'graph_tag'})
    l_ko_str = l_outcomes[0].text.split('KO/TKO')[0]
    l_submission_str = l_outcomes[1].text.split('SUBMISSIONS')[0]
    l_decision_str = l_outcomes[2].text.split('DECISIONS')[0]

    w_ko = int(w_ko_str)
    w_submission = int(w_submission_str)
    w_decision = int(w_decision_str)
    l_ko = int(l_ko_str)
    l_submission = int(l_submission_str)
    l_decision = int(l_decision_str)

    record = FighterRecord(w_ko, w_submission, w_decision, l_ko, l_submission, l_decision)

    return Fighter(ref=ref, name=name, country=country, city=city, birthday=birthday, height=height,
                   weight=weight, record=str(record))


def _parse_opponents(parsed_html):
    history_tags = parsed_html.body.findAll('div', attrs={'class': 'module fight_history'})
    history_tag = filter(lambda tag: tag.findAll('h2', text='Fight History'), history_tags)[0]

    opponents_rows = history_tag.findAll('tr')[1:]
    opponents_pages = [row.findAll('td')[1].a['href'] for row in opponents_rows]

    for page in opponents_pages:
        print(page)
