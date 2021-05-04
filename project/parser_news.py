import requests
from bs4 import BeautifulSoup
import time
from enum import Enum


class Completeness_of_search(Enum):
    ONLY_TITLE = 1
    WITH_SHORT_NEWS = 2
    FULL_INFO = 3


class Parser:
    def __init__(self):
        self.pars = 'html.parser'
        self.URL = 'https://www.interfax.ru/story/'
        self.common_url = 'https://www.interfax.ru'
        self.items_list = []
        self.complet_of_search_parser = 0
        self.num_topics_search = -1
        self.num_docs_in_topics_search = -1
        self.common_requested_num_topics = 0
        self.common_requested_num_docs = 0

    def get_html(self, url):
        response = ''
        while response == '':
            try:
                response = requests.get(url)
                break
            except:
                time.sleep(5)
                continue

        response.encoding = 'cp1251'
        return response

    def get_soup(self, url):
        html = self.get_html(url)

        if html.status_code == 200:
            soup = BeautifulSoup(html.text, self.pars)
            return soup

    def get_content(self, complet_of_search):
        soup = self.get_soup(self.URL)

        items_html = soup.find_all('div', class_="allStory")

        for item_all_story in items_html:
            item_common = item_all_story.find_all('div', recursive=False)

            for item in item_common:
                if self.common_requested_num_topics != -1:
                    if self.common_requested_num_topics == 0:
                        return
                    else:
                        self.common_requested_num_topics -= 1

                title = item.find('div', class_="title").find('a').get_text(strip=True)
                description = item.find('span', class_="text").get_text(strip=True)
                link = item.find('div', class_="title").find('a').get('href')
                if link[0] == '/':
                    link = self.common_url + link

                num_docs = item.find('div', class_="info").find('a').get_text(strip=True)
                last_update = item.find('div', class_="info").find('time').get_text(strip=True)

                try:
                    img = item.find('a').find('img').get('src').replace('\t', '')
                except:
                    img = ''

                docs_list = []

                if complet_of_search != Completeness_of_search.ONLY_TITLE:
                    self.get_add_content_from_news_title(link, docs_list, complet_of_search,
                                                         self.common_requested_num_docs)

                self.items_list.append({
                    'title': title,
                    'description': description,
                    'link': link,
                    'num_docs': num_docs,
                    'last_update': last_update,
                    'img': img,
                    'docs': docs_list
                })

    def get_add_content_from_news_title(self, link, docs_list, complet_of_search, requested_num_docs = -1):
        soup_title = self.get_soup(link)

        timelines_newsgroups = soup_title.find_all('div', class_="timeline")

        all_news_in_newsgroup = None

        if len(timelines_newsgroups) == 0:
            timelines_newsgroups = soup_title.find('div', class_="storyList").find_all('div', recursive=False)

        for newsgroup in timelines_newsgroups:
            try:
                date_newsgroup = newsgroup.find('span', recursive=False).get_text(strip=True)
            except:
                date_newsgroup = ''
                lst = []
                all_news_in_newsgroup = lst.append(newsgroup)

            if not all_news_in_newsgroup:
                all_news_in_newsgroup = newsgroup.find_all('section', class_="chronicles__item chronicles__big")

            for news in all_news_in_newsgroup:
                if requested_num_docs != -1:
                    if requested_num_docs == 0:
                        return
                    else:
                        requested_num_docs -= 1

                time_news = news.find('time').get_text(strip=True)

                try:
                    link_full_news = news.find('a').get('href')

                    if link_full_news[0] == '/':
                        link_full_news = self.common_url + link_full_news
                except:
                    link_full_news = ''

                try:
                    title_news = news.find('a').find('h3').get_text(strip=True)
                except:
                    try:
                        title_news = news.find('h3').get_text(strip=True)
                    except:
                        title_news = news.find('h2').get_text(strip=True)

                short_text = ''
                try:
                    for i in news.find_all('p'):
                        short_text += (i.get_text(strip=True) + '\n')
                except:
                    short_text = ''

                if complet_of_search == Completeness_of_search.FULL_INFO and link_full_news is not None:
                    soup_full_news = self.get_soup(link_full_news)

                    full_text = soup_full_news.find(
                        'div', class_="mainblock"
                    ).find('article', itemprop="articleBody").get_text()
                else:
                    full_text = short_text

                docs_list.append({
                    'title_news': title_news,
                    'time_news': date_newsgroup + " " + time_news,
                    'link_full_news': link_full_news,
                    'short_text': short_text,
                    'full_text': full_text
                })

    def parse(self, complet_of_search, requested_num_topics = -1, requested_num_docs = -1):
        self.items_list = []

        soup = self.get_soup(self.URL)
        items_pages = soup.find('div', class_="mainblock").find('div', class_="allPNav").find_all('a')
        num_pages = int(items_pages[-1].get_text(strip=True))

        self.complet_of_search_parser = complet_of_search
        self.num_topics_search = requested_num_topics
        self.num_docs_in_topics_search = requested_num_docs
        self.common_requested_num_topics = requested_num_topics
        self.common_requested_num_docs = requested_num_docs

        for num_cur_page in range(num_pages):
            if self.common_requested_num_topics == 0:
                break

            html = self.get_html(self.URL + 'page_{}'.format(num_cur_page + 1))

            if html.status_code == 200:
                self.get_content(complet_of_search)

    def drop_parser(self):
        self.items_list = []
        self.complet_of_search_parser = 0
        self.num_topics_search = -1
        self.num_docs_in_topics_search = -1
        self.common_requested_num_topics = 0
        self.common_requested_num_docs = 0
