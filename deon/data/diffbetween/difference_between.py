from deon.data.datasource import DataSource
from urllib.request import Request, urlopen
from bs4 import BeautifulSoup
from pathlib import Path
import deon.data.util as util

import time
import os
import re

from deon.data.diffbetween.difference_between_definition import DifferenceBetween


class DiffBetweenDataSource(DataSource):
    """DataSource implementation for the w00 dataset."""

    KEY = 'diffbetween'
    _PAGE_FOLDER = 'diffbetween'
    _OUT_FILE = 'diffbetween.tsv'
    BLACKLIST = ['he','she','it','this','these','therefore','they','her','his','posted on','difference','help us', 'although', 'those', 'CC BY']
    f_out_path = ''

    def pull(self, dest):
        print('Pulling from diffbetween dataset...')

        self.f_out_path = os.path.join(dest, self._OUT_FILE)
        folder_path = '{}/{}'.format(dest, self._PAGE_FOLDER)
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)

        self._save_locally(folder_path)
        print('\n')
        self._extract_from(folder_path)
        print('\n\tDONE\n')
        return self.f_out_path

    def _save_locally(self, folder_path):
        try:
            url = 'http://www.differencebetween.com/page/1/'
            saved_links = set(os.listdir(folder_path))
            i = 0
            while url is not None:
                page = self._getHtmlPage(url)
                soup_page = BeautifulSoup(page, 'html5lib')
                articles = soup_page.find_all('article')

                links = [self._extractLink(article) for article in articles]
                for link in links:
                    i += 1
                    util.print_progress('Saving locally ({})'.format(len(saved_links)), i)

                    if link in saved_links:
                        continue

                    self._savePage(link, folder_path)
                    saved_links.add(self._get_name_from(link))
                    time.sleep(1)

                url = self._getNextUrl(soup_page)
                time.sleep(2)
        except:
            print('\tSomething wrong happend processing {}'.format(url))
            print('\tRetrying again in 5 seconds...')
            time.sleep(5)
            self._save_locally(folder_path)

    def _extract_from(self, folder_path):
        files = os.listdir(folder_path)
        for i, file_name in enumerate(files):
            util.print_progress('Extracting def/nodef ', i + 1, len(files))

            file_path = '{}/{}'.format(folder_path, file_name)
            try:
                article = BeautifulSoup(open(file_path), "html.parser")\
                          .find('article')
                topics = self._extractTopics(article, file_name)
                # defs = self._extract_topics_definitions_from(article, topics)
                # for _def in defs:
                #     self._saveOutput(_def[0], _def[1], _def[2], 1, file_name)
                # print(file_name)
                nodefs = self._extract_no_def_from_file(article, topics)
                for _nodef in nodefs:
                    self._saveOutput(_nodef, '?', '?', 0, file_name)
            except:
                print('Smth wrong with', file_path)

    def _pageExist(self, link, folder_path):
        file_name = link.split('/')[-2]
        file = Path('{}/{}'.format(folder_path, file_name))
        return file.is_file()

    def _get_name_from(self, link):
        return link.split('/')[-2]

    def _savePage(self, link, folder_path):
        file_name = self._get_name_from(link)
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

    def _extract_no_def_from_file(self, article, topics):
        nodef_ls = []
        article_txt = ' '.join([p.get_text() for p in article.find_all('p')])
        article_txt = ' '.join(article_txt.split())
        for sentence in re.split('[?!.:]+ ', article_txt):
            sentence = ' '.join(sentence.split())
            _sentence = set(sentence.lower().replace(',', ' ').split())
            _topics = set([item for sublist in [top.split() for top in topics] for item in sublist])

            if _topics.intersection(_sentence):
                continue

            if len(_sentence) < 4:
                continue

            sentence = re.sub('[^\w,.\' /\\()-]', '', sentence).strip()
            if sentence.lower().startswith(tuple(self.BLACKLIST)):
                continue

            nodef_ls.append(sentence)
        return nodef_ls

    def _is_a_definition(self, topic, sentence):
        return re.match(r"^((a)|(an) )?{} ((is)|(are)).+"
                .format(topic), sentence)

    def _topic_position(self, topic, sentence):
        pos = [str(x) for x in range(sentence.find(topic), len(topic.split()))]
        return ','.join(pos)

    def _extract_topics_definitions_from(self, article, topics):
        result = []
        definitions = DifferenceBetween(article, topics).extractDefinitions()

        for topic in topics:
            for _def in definitions.values():
                if _def is None:
                    continue
                lower_def = _def.lower()

                if re.match(r"^((a)|(an) )?{} ((is)|(are)).+".format(topic), lower_def):
                    pos = [str(x) for x in range(lower_def.find(topic), len(topic.split()))]
                    pos = ','.join(pos)
                    result.append((_def, topic, pos))
                    break
        return result

    def _extractTopics(self, article, file_name):
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

        _topic = file_name.replace('difference-between-', '')
        _topic = _topic.split('-and-vs-')
        for _t in _topic:
            topics.append(_t.replace('-', ' '))

        return topics

    def _saveOutput(self, definition, topic, topic_pos, _def, url):
        with open(self.f_out_path, 'a') as f:
            f.write('{}\t{}\t{}\t{}\t{}\n'.format(definition, topic, topic_pos, _def, url))

    def _extractLink(self, article):
        return article.find('header').find('a').get('href')
