from deon.data.datasource import DataSource
from bs4 import BeautifulSoup
import deon.util as util

import os
import re

from deon.data.diffbetween.definitions import DifferenceBetween
from deon.data.diffbetween.downloader import Downloader
from deon.data.txt_classifier import TxtClassifier


class DiffBetweenDataSource(DataSource):
    """DataSource implementation for the w00 dataset."""

    KEY = 'diffbetween'
    _PAGE_FOLDER = 'diffbetween'
    _OUT_FILES = ['diffbetween.def.tsv', 'diffbetween.nodef.tsv', 'diffbetween.anafora.tsv']

    def pull(self, dest, download):
        print('Pulling from diffbetween dataset...')
        self.dest = dest
        self.f_out_path = os.path.join(dest, self._OUT_FILES[0])
        folder_path = '{}/{}'.format(dest, self._PAGE_FOLDER)
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)

        if download:
            downloader = Downloader(folder_path)
            downloader.save_locally()
            print('\n')

        if util.tsv_already_exist(dest, self._OUT_FILES):
            return

        self._extract_from(folder_path)
        print('\n\tDONE\n')
        return



    def _extract_from(self, folder_path):
        # wcl_process = util.start_wcl_process()
        classifier = TxtClassifier()
        files = os.listdir(folder_path)
        for i, file_name in enumerate(files):
            util.print_progress('Extracting def/nodef ', i + 1, len(files))

            file_path = '{}/{}'.format(folder_path, file_name)
            article = BeautifulSoup(open(file_path), "html.parser").find('article')
            topics = self._extract_topics(article, file_name)
            content = self._extract_text(article)

            defs_set = self._extract_topics_definitions_from(article, topics)
            classifier_result = classifier.classify(content, topics)
            classifier_result['def'].union(defs_set)

            for topic, sentence in classifier_result['def']:
                pos = util.topic_position(topic, sentence)
                _topic = topic
                if not pos:
                    pos = '?'
                    _topic = '?'
                self._save_def(sentence, file_name, _topic, pos)
            for topic, sentence in classifier_result['nodef']:
                pos = util.topic_position(topic, sentence)
                _topic = topic
                if not pos:
                    pos = '?'
                    _topic = '?'
                self._save_nodef(sentence, file_name, _topic, pos)
            for topic, sentence in classifier_result['anafora']:
                self._save_anafora(sentence, file_name)

    def _save_def(self, sentence, url, topic, pos):
        out_file = os.path.join(self.dest, self._OUT_FILES[0])
        util.save_output(out_file, sentence, '1', url, topic, pos)

    def _save_nodef(self, sentence, url, topic='?', pos='?'):
        out_file = os.path.join(self.dest, self._OUT_FILES[1])
        util.save_output(out_file, sentence, '0', url, topic, pos)

    def _save_anafora(self, sentence, url):
        out_file = os.path.join(self.dest, self._OUT_FILES[2])
        util.save_output(out_file, sentence, '0', url, '?', '?')

    def skip(self, sentence):
        return self._is_in_blacklist(sentence)

    def _is_in_blacklist(self, sentence):
        blacklist = ('therefore', 'posted on', 'difference', 'help us', 'although',
            'those', 'CC', 'facebook', 'however', 'accessed',
            'structural formulae')
        sentence = sentence.lower()
        return sentence.startswith(blacklist)

    def _extract_text(self, article):
        ps = [p.get_text() for p in article.find_all('p') if not p.strong]
        article_txt = ' '.join(ps)
        article_txt = ' '.join(article_txt.split())
        return article_txt

    def _extract_topics_definitions_from(self, article, topics):
        result = set()
        definitions = DifferenceBetween(article, topics).extractDefinitions()

        for topic in topics:
            for _def in definitions.values():
                if _def is None:
                    continue
                lower_def = _def.lower()

                if re.match(r"^((a)|(an) )?{} ((is)|(are)).+".format(topic), lower_def):
                    result.add((topic, ' '.join(util.tokenize(_def))))
                    break
        return result

    def _extract_topics(self, article, file_name):
        topics = set()
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

            topics.add(topic)

        _topic = file_name.replace('difference-between-', '')
        _topic = _topic.split('-and-vs-')
        for _t in _topic:
            topics.add(_t.replace('-', ' '))

        return topics
