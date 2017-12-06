import os
from bs4 import BeautifulSoup
import deon.util as util
import time
from urllib.request import Request, urlopen


class Downloader():

    def __init__(self, folder_path):
        self.folder_path = folder_path

    def save_locally(self, url='http://www.differencebetween.com/page/1/'):
        try:
            saved_links = set(os.listdir(self.folder_path))
            i = 0
            tries = 0
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

                    self._savePage(link, self.folder_path)
                    saved_links.add(self._get_name_from(link))

                url = self._getNextUrl(soup_page)
                time.sleep(1)
        except:
            print('\tSomething wrong happend processing {}'.format(url))
            print('\tRetrying again in 5 seconds...')
            time.sleep(5)
            tries += 1
            if tries > 5:
                tries = 0
                url = self._getNextUrl(soup_page)
            self._save_locally(url)

    def _savePage(self, link):
        file_name = self._get_name_from(link)
        page = self._getHtmlPage(link)
        f_out_path = os.path.join(self.folder_path, file_name)
        with open(f_out_path, 'wb') as f:
            f.write(page)

    def _get_name_from(self, link):
        return link.split('/')[-2]

    def _getHtmlPage(self, link):
        headers = {'User-Agent': 'Mozilla/5.0'}
        return urlopen(Request(link, headers=headers)).read()

    def _getNextUrl(self, page):
        li = page.find("li", {"class": "pagination-next"})
        if li is None:
            return None
        return li.find('a').get('href')

    def _extractLink(self, article):
        return article.find('header').find('a').get('href')
