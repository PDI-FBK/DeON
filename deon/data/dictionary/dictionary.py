from deon.data.datasource import DataSource
from urllib.request import Request, urlopen
from bs4 import BeautifulSoup
import os
import time
import pickle

from deon.data.dictionary.dictionary_definition import Dictionary


class DictionarySource(DataSource):
    KEY = 'dictionary'
    _LINK = 'http://www.dictionary.com'
    _PAGE_FOLDER = 'dictionary'
    _OUT_FILE = '{}.tsv'.format(KEY)
    f_out_path = ''

    def pull(self, dest):
        print('Pulling for dictionary dataset...')
        self.f_out_path = os.path.join(dest, self._OUT_FILE)
        folder_path = '{}/{}'.format(dest, self._PAGE_FOLDER)
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)

        self._save_locally(folder_path)
        self._extract_topics_definitions_from(folder_path)
        return self.f_out_path

    def _save_locally(self, folder_path):
        count = 0
        try:
            saved_links = self._saved_links(folder_path)
            url = ''
            for letter in range(ord('a'), ord('z') + 1):
                url = '{}/list/{}'.format(self._LINK, chr(letter))
                page = BeautifulSoup(self._get_html_page(url), 'html5lib')
                total_pages = self._get_last_number(page)
                print("{} - [{}]".format(chr(letter), total_pages))

                for i in range(2, total_pages + 1):
                    definition_urls = self._get_word_defs(page)
                    for link in definition_urls:
                        if link in saved_links:
                            continue
                        self._save_page(folder_path, link)
                        saved_links.add(link)

                    next_url = '{}/list/{}/{}'\
                              .format(self._LINK, chr(letter), i)
                    page = BeautifulSoup(self._get_html_page(next_url), 'html5lib')
                    time.sleep(2)
        except:
            pickle.dump(saved_links, open("{}/processed_links".format(folder_path), "wb"))
            print('\tSomething wrong happend processing {}'.format(url))
            print('\tRetrying again in 5 seconds...')
            time.sleep(5)
            self._saveLocally(folder_path)

    def _extract_topics_definitions_from(self, folder):
        for file_name in os.listdir(folder):
            try:
                self._extract_from_file('{}/{}'.format(folder, file_name))
            except:
                print("Failed to process " + file_name)

    def _saved_links(self, folder_path):
        try:
            saved_links = pickle.load(open("{}/processed_links".format(folder_path), "rb"))
        except (OSError, IOError):
            saved_links = set()
        return saved_links

    def _get_html_page(self, link):
        return urlopen(Request(link, headers={'User-Agent': 'Mozilla/5.0'})).read()

    def _get_last_number(self, page):
        pagination = page.find('div', {'class': 'pagination'})
        last_href = pagination.find_all('a')[-1]
        if '>>' in last_href.get_text():
            next_page = self._get_html_page(last_href['href'])
            next_page = BeautifulSoup(next_page, 'html5lib')
            return self._get_last_number(next_page)
        nr = int(last_href['href'].split('/')[-1])
        return nr

    def _get_word_defs(self, page):
        span = page.find_all('span', {'class': 'word'})
        return [s.find('a')['href'] for s in span]

    def _save_page(self, folder_path, link):
        file_name = link.split('/')[-1]
        page = self._get_html_page(link)
        file_path = '{}/{}'.format(folder_path, file_name)
        with open(file_path, 'wb') as f:
            f.write(page)

    def _extract_from_file(self, file_name):
        dictionary = Dictionary(file_name)
        definitions = dictionary.extract_definition()
        for dict_def in definitions:
            for topic, def_list in dict_def.items():
                for _def in def_list:
                    pos = ','.join(
                      [str(x) for x in range(_def.find(topic), len(topic.split()))])
                    self._save_definition_output(_def, topic, pos, file_name)

    def _save_definition_output(self, definition, topic, topic_pos, url):
        with open('{}'.format(self.f_out_path), 'a') as f:
            url = "{}/browse/{}".format(self._LINK, url)
            f.write('{}\t{}\t{}\t{}\n'.format(definition, topic, topic_pos, url))
