import time
import urllib

from BeautifulSoup import BeautifulSoup
from storage.models.fighter import Fighter
from storage.models.fight import Fight
from storage.models.event import Event


def parse_fighter_page(url):
    socket = urllib.urlopen(url)
    page = socket.read()
    parsed_html = BeautifulSoup(page)

    fighter = _parse_fighter(url, parsed_html)
    _parse_opponents(parsed_html)

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

    return Fighter(ref=ref, name=name, country=country, city=city, birthday=birthday, height=height,
                   weight=weight)


def _parse_opponents(parsed_html):
    history_tags = parsed_html.body.findAll('div', attrs={'class': 'module fight_history'})
    history_tag = filter(lambda tag: tag.findAll('h2', text='Fight History'), history_tags)[0]

    opponents_rows = history_tag.findAll('tr')[1:]
    opponents_pages = [row.findAll('td')[1].a['href'] for row in opponents_rows]

    for page in opponents_pages:
        print(page)
