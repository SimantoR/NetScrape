
from sys import argv, stderr
import json

with open('.conf', 'rb') as conf_file:
    CONF = json.load(conf_file)


debug_mode = True if '-v' in argv else False


def parse_article(url):
    from bs4 import BeautifulSoup, Tag
    from datetime import datetime
    from unidecode import unidecode
    import requests

    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')

        title_tag: Tag = soup.find('h1', class_='single-heading')
        title: str = unidecode(title_tag.decode_contents())

        # title and date-time are under same parent
        timestamp = title_tag.parent.findChild('p').find('span', class_='p3')
        timestamp = timestamp.text
        timestamp = timestamp.replace(timestamp.rsplit()[0], '').strip()
        timestamp = datetime.strptime(timestamp, '%B %d, %Y %H:%M:%S')

        # content
        content_tag: Tag = soup.find(
            'div', attrs={'class': 'card-content', 'id': 'content-part'})
        p_tags = content_tag.find_all('p')
        article = str()
        for p in p_tags:
            # get text from the tag
            p = p.text
            # fix any encoding problems
            p: str = unidecode(p)
            # strip any unnecessary whitespaces
            p.strip()
            article += p + '\n'

        if debug_mode:
            print('Title: '+title)
            print('Timestamp: '+timestamp.date())

        return title, article, timestamp


def crawl():
    from bs4 import BeautifulSoup, Tag
    from datetime import datetime
    import json
    import requests

    response = requests.get(
        'https://thefinancialexpress.com.bd/page/stock/bangladesh')

    if response.status_code == 200:
        soup = BeautifulSoup(
            response.content, 'html.parser', from_encoding='utf-8')
        link_tags = soup.find_all('a', href=True)
        unique_links = set()

        for a in link_tags:
            link: str = a['href']
            if (link.startswith('https://thefinancialexpress.com.bd/stock/') and link not in unique_links):
                unique_links.add(link)
                title, article, timestamp = parse_article(link)
                yield title, article, None, timestamp, link
        del unique_links


if __name__ == '__main__':
    crawl()
