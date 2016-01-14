import urllib
import time

from fighter import Fighter
from BeautifulSoup import BeautifulSoup

def parse_fighter_page(url):
    socket = urllib.urlopen(url)
    page = socket.read()
    parsed_html = BeautifulSoup(page)

    fighter = _parse_fighter(parsed_html)
    _parse_opponents(parsed_html)

    print(fighter.birthday)
    socket.close()


def _parse_fighter(parsed_html):
    name = parsed_html.body.find('span', attrs={'class': 'fn'}).text

    birthday_str = parsed_html.body.find('span', attrs={'itemprop': 'birthDate'}).text
    birthday = time.strptime(birthday_str, "%Y-%m-%d")

    city = parsed_html.body.find('span', attrs={'itemprop': 'addressLocality'}).text
    country = parsed_html.body.find('strong', attrs={'itemprop': 'nationality'}).text

    height_str = parsed_html.body.find('span', attrs={'class': 'item height'}).contents[-1]
    height = float(height_str.strip().split(' ')[0])

    return Fighter(name, country, city, birthday, height)


def _parse_opponents(parsed_html):
    history_tags = parsed_html.body.findAll('div', attrs={'class': 'module fight_history'})
    history_tag = history_tags[-1]

    for row in history_tag.findAll('tr')[1:]:
        print(row.findAll('td')[1].a['href'])
