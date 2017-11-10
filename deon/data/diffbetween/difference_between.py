from deon.data.datasource import DataSource
from urllib.request import Request, urlopen
from bs4 import BeautifulSoup
from pathlib import Path

import time
import pickle
import os
import re

from deon.data.diffbetween.difference_between_definition import DifferenceBetween


class DiffBetweenDataSource(DataSource):
    """DataSource implementation for the w00 dataset."""

    KEY = 'diffbetween'
    _PAGE_FOLDER = 'diffbetween'
    _OUT_FILE = 'diffbetween.tsv'
    f_out_path = ''

    def pull(self, dest):
        print('Pulling for diffbetween dataset...')
        self.f_out_path = os.path.join(dest, self._OUT_FILE)
        folder_path = '{}/{}'.format(dest, self._PAGE_FOLDER)
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)

        self._saveLocally(folder_path)
        self._extractTopicsDefinitionsFrom(folder_path)

        return self.f_out_path

    def _saveLocally(self, folder_path):
        count = 0
        try:
            url = 'http://www.differencebetween.com/page/1/'
            saved_links = self._savedLinks(folder_path)
            while url is not None and count < 2:
                count += 1
                print('\r\t{}'.format(url))
                page = self._getHtmlPage(url)
                soup_page = BeautifulSoup(page, 'html5lib')
                articles = soup_page.find_all('article')

                links = [self._extractLink(article) for article in articles]
                for link in links:
                    if link in saved_links:
                        continue
                    if self._pageExist(link, folder_path):
                        saved_links.add(link)
                        continue

                    self._savePage(link, folder_path)
                    saved_links.add(link)
                    time.sleep(1)

                url = self._getNextUrl(soup_page)
                time.sleep(2)
        except:
            pickle.dump(saved_links, open("{}/processed_links".format(folder_path), "wb" ))
            print('\tSomething wrong happend processing {}'.format(url))
            print('\tRetrying again in 5 seconds...')
            time.sleep(5)
            self._saveLocally(folder_path)

    def _pageExist(self, link, folder_path):
        file_name = link.split('/')[-2]
        file = Path('{}/{}'.format(folder_path, file_name))
        return file.is_file()

    def _savePage(self, link, folder_path):
        file_name = link.split('/')[-2]
        page = self._getHtmlPage(link)
        f_out_path = os.path.join(folder_path, file_name)
        with open(f_out_path, 'wb') as f:
            f.write(page)

    def _getNextUrl(self, page):
        li = page.find("li", {"class": "pagination-next"})
        if li is None:
            return None
        return li.find('a').get('href')

    def _getHtmlPage(self, link):
        return urlopen(Request(link, headers={'User-Agent': 'Mozilla/5.0'})).read()


    def _extractTopicsDefinitionsFrom(self, folder_path):
        for file_name in os.listdir(folder_path):
            article = BeautifulSoup(open('{}/{}'\
                      .format(folder_path, file_name)), "html.parser")\
                      .find('article')
            topics = self._extractTopics(article)
            definitions = DifferenceBetween(article, topics).extractDefinitions()

            for topic in topics:
                for _def in definitions.values():
                    if _def is None:
                        continue
                    lower_def = _def.lower()

                    if re.match(r"^((a)|(an) )?{} ((is)|(are)).+".format(topic), lower_def):
                        pos = [str(x) for x in range(lower_def.find(topic), len(topic.split()))]
                        pos = ','.join(pos)
                        self._saveDefinitionOutput(_def, topic, pos, file_name)
                        break

    def _extractTopics(self, article):
        topics = []
        h2s = article.find_all('h2')
        ps = article.find_all('p')
        tags = h2s + ps
        for tag in tags:
            tagtxt = ' '.join(tag.get_text().lower().split())
            topic = ''
            if (tagtxt.startswith('what is') and 'etween' not in tagtxt) or\
               (tagtxt.startswith('what are') and 'etween' not in tagtxt):
                topic = tagtxt.split()[2:]
            elif tagtxt.startswith('what does'):
                topic = tagtxt.split()[2:-1]

            topic = ' '.join(topic).replace('?', '')
            if topic == '':
                continue

            words = topic.split()
            if words[0] == 'a' or words[0] == 'an':
                topic = ' '.join(words[1:])

            topics.append(topic)
        return topics

    def _saveDefinitionOutput(self, definition, topic, topic_pos, url):
        with open(self.f_out_path, 'a') as f:
            f.write('{}\t{}\t{}\t{}\t{}\n'.format(definition, topic, topic_pos, 1, url))

    def _savedLinks(self, folder_path):
        try:
            saved_links = pickle.load(open("{}/processed_links".format(folder_path), "rb" ) )
        except (OSError, IOError):
            saved_links = set()
        return saved_links

    def _extractLink(self, article):
        return article.find('header').find('a').get('href')
