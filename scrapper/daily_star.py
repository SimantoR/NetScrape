from bs4 import BeautifulSoup, Tag
from datetime import datetime
from sys import argv, stderr
from uuid import uuid5, NAMESPACE_DNS
import json, sqlite3, requests, re

# constant properties
BASE_URL = 'https://www.thedailystar.net'
BUSINESS_URL = BASE_URL+'/business'

with open('.conf', 'rb') as json_file:
    CONF = json.load(json_file)

debug_mode = True if '-v' in argv else False

if debug_mode:
    print('::\tDate\t::\tAuthor\t::\tArticle\t::\n')


def parse_article(url):
    from unidecode import unidecode

    url = BASE_URL+url
    # print(url)
    response: requests.Response = requests.get(url)
    if (response.status_code == 200):
        soup = BeautifulSoup(response.content, 'html.parser')

        ### get title ###
        title: Tag = soup.find('h1', attrs={'itemprop': 'headline'})
        title = title.decode_contents(eventual_encoding='utf-32')

        ### get author ###
        all_links: Tag = soup.find_all('a', href=True)  # find all links
        author = str()
        for a in all_links:  # iterate through all links and find one which starts with '/author'
            a: Tag = a
            link: str = a['href']
            if (link.startswith('/author')):
                author = a.decode_contents(eventual_encoding='utf-32')
                break
        if author == '':
            author = None

        ### get time ###
        date = soup.find('meta', {'itemprop': 'datePublished'})
        # stip any extra spaces
        date = date['content'].strip()
        # parse into datetime object
        date: datetime = datetime.strptime(date, "%Y-%m-%dT%H:%M:%S+06:00")

        ### get article content ###
        article_tag: Tag = soup.find('div', {'class': 'node-content'})
        # find all paragraphs
        # article = article_tag.getText(separator=' ', strip=True)
        p_tags = article_tag.find_all('p')
        article = ''
        for p in p_tags:
            # extract content from the tag
            p = p.decode_contents()
            # fix any encoding problems
            p = unidecode(p)
            # strip any unnecessary whitespaces
            p.strip()
            article += p + '\n'

        if debug_mode:
            print(
                f'{date.date()}::\t{author if author != None else "[---------]"}\t::\t{title}')
        return title, article, author, date


# get all news article links from front-page
def crawl():
    response = requests.get(url=BUSINESS_URL)
    if (response.status_code):
        soup = BeautifulSoup(markup=response.content, features='html.parser', from_encoding='utf-32')

        # get all <a/> html tags
        tags = soup.find_all('a', href=True)
        # a new set to store unique links

        # get href value from each <a/> tag
        for a in tags:
            link: str = a['href']

            # check if it is a business article link and a unique one
            if (link.startswith('/business') and 'news' in link):
                # add the unique article link
                # unique_links.add(link)
                title, article, author, timestamp = parse_article(link)
                yield title, article, author, timestamp, BASE_URL+link