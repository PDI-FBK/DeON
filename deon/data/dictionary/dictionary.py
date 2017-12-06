from deon.data.datasource import DataSource
from urllib.request import Request, urlopen, HTTPError, URLError
from bs4 import BeautifulSoup
import os
import time
import deon.util as util

from deon.data.dictionary.dictionary_definition import Dictionary


class DictionarySource(DataSource):
    KEY = 'dictionary'
    _LINK = 'http://www.dictionary.com'
    _PAGE_FOLDER = 'dictionary'
    _WCL_OUT_FILE = ['dictionary.wcl.def.tsv', 'dictionary.wcl.nodef.tsv']

    def pull(self, dest, download):
        print('Pulling for dictionary dataset...')
        self.wcl_process = util.start_wcl_process()
        self.dest = dest

        folder_path = '{}/{}'.format(dest, self._PAGE_FOLDER)
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)

        if download:
            self._save_locally(folder_path)

        if util.tsv_already_exist(dest, self._WCL_OUT_FILE):
            return

        self._extract_topics_definitions_from(folder_path)
        return

    def _save_locally(self, folder_path, start='a', end='z'):
        count = 0
        _start = start
        _end = end
        try:
            saved_links = set(os.listdir(folder_path))
            url = ''
            current_letter = _start
            for letter in range(ord(_start), ord(_end) + 1):
                current_letter = letter
                url = '{}/list/{}'.format(self._LINK, chr(letter))
                page = BeautifulSoup(self._get_html_page(url), 'html5lib')
                total_pages = self._get_last_number(page)
                print("{} - [{}]".format(chr(letter), total_pages))

                for i in range(2, total_pages + 1):
                    definition_urls = self._get_word_defs(page)
                    for link in definition_urls:
                        count += 1
                        util.print_progress('Saving locally ({})'
                            .format(len(saved_links)), count)

                        if link in saved_links:
                            continue
                        self._save_page(folder_path, link)
                        saved_links.add(self._get_name_from(link))

                    next_url = '{}/list/{}/{}'\
                              .format(self._LINK, chr(letter), i)
                    page = BeautifulSoup(self._get_html_page(next_url), 'html5lib')
                    time.sleep(2)
        except (HTTPError, URLError) as error:
            print('\t{} {}'.format(error, url))
            print('\tRetrying again in 5 seconds...')
            time.sleep(5)
            self._saveLocally(folder_path, current_letter)
        return

    def _extract_topics_definitions_from(self, folder):
        files = os.listdir(folder)
        count_failed = 0
        for i, file_name in enumerate(files):
            try:
                self._extract_from_file('{}/{}'.format(folder, file_name))
            except:
                count_failed += 1

            util.print_progress('Extracting def/nodef ', i + 1, len(files), count_failed)
        return

    def _get_html_page(self, link):
        return urlopen(Request(link, headers={'User-Agent': 'Mozilla/5.0'})).read()

    def _get_last_number(self, page):
        nr = 0
        pagination = page.find('div', {'class': 'pagination'})
        if not pagination:
            return nr
        last_href = pagination.find_all('a')[-1]
        if '>>' in last_href.get_text():
            next_page = self._get_html_page(last_href['href'])
            next_page = BeautifulSoup(next_page, 'html5lib')
            return self._get_last_number(next_page)
        nr = int(last_href['href'].split('/')[-1])
        return nr

    def _get_word_defs(self, page):
        try:
            span = page.find_all('span', {'class': 'word'})
            return [s.find('a')['href'] for s in span]
        except:
            return []

    def _get_name_from(self, link):
        return link.split('/')[-1]

    def _save_page(self, folder_path, link):
        file_name = self._get_name_from(link)
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
                    pos = util.topic_position(topic.lower(), _def.lower())
                    if not pos:
                        continue
                    self._ask_wcl_wrapper(_def, topic, pos, file_name)

    def _ask_wcl_wrapper(self, definition, topic, topic_pos, url):
        _def = util.query_wcl_for(self.wcl_process, topic.lower(), definition.lower())
        if _def:
            out_file = os.path.join(self.dest, self._WCL_OUT_FILE[0])
            util.save_output(out_file, definition, '1', url, topic, topic_pos)
        else:
            out_file = os.path.join(self.dest, self._WCL_OUT_FILE[1])
            util.save_output(out_file, definition, '0', url, topic, topic_pos)
