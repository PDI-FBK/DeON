from deon.data.datasource import DataSource
from bs4 import BeautifulSoup
import deon.data.util as util

import os
import re

from deon.data.diffbetween.definitions import DifferenceBetween
from deon.data.diffbetween.no_definitions import NoDefinitions
from deon.data.diffbetween.downloader import Downloader


class DiffBetweenDataSource(DataSource):
    """DataSource implementation for the w00 dataset."""

    KEY = 'diffbetween'
    _PAGE_FOLDER = 'diffbetween'
    _OUT_FILES = ['diffbetween.def.tsv', 'diffbetween.nodef.tsv', 'diffbetween.anafora.tsv', 'diffbetween.wcl.tsv']

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

        self._extract_from(folder_path)
        print('\n\tDONE\n')
        return self.f_out_path



    def _extract_from(self, folder_path):
        wcl_process = util.start_wcl_process()
        files = os.listdir(folder_path)
        for i, file_name in enumerate(files):
            util.print_progress('Extracting def/nodef ', i + 1, len(files))

            file_path = '{}/{}'.format(folder_path, file_name)
            article = BeautifulSoup(open(file_path), "html.parser").find('article')
            topics = self._extractTopics(article, file_name)

            defs = self._save_defs(article, topics, file_name)

            no_definition = NoDefinitions(article, topics)
            self._save_nodefs(no_definition, file_name)
            self._save_properties(wcl_process, no_definition, set(defs), file_name)
            self._save_anafora(no_definition, file_name)

    def _save_defs(self, article, topics, file_name):
        defs = self._extract_topics_definitions_from(article, topics)
        file = os.path.join(self.dest, self._OUT_FILES[0])
        for _def in defs:
            util.save_output(file, _def[0], 1, file_name, _def[1], _def[2])
        return defs

    def _save_nodefs(self, no_definition, file_name):
        nodefs = no_definition.extract_no_def()
        file = os.path.join(self.dest, self._OUT_FILES[1])
        for _nodef in nodefs:
            util.save_output(file, _nodef, 0, file_name, '?', '?')
        return nodefs

    def _save_properties(self, wcl_process, no_definition, defs, file_name):
        properties = no_definition.extract_no_def_properties(defs)
        file = os.path.join(self.dest, self._OUT_FILES[3])
        for p in properties:
            sentence = p[0]
            topic = p[1]
            pos = util.topic_position(topic, sentence.lower())
            if pos:
                _def = util.query_wcl_for(wcl_process, topic, sentence)
                _def = 1 if _def else 0
                util.save_output(file, sentence, _def, file_name, topic, pos)

        return properties

    def _save_anafora(self, no_definition, file_name):
        anaforas = no_definition.extract_anafora()
        file = os.path.join(self.dest, self._OUT_FILES[2])
        for anaf in anaforas:
            util.save_output(file, anaf, '?', file_name, '?', '?')

    def _extract_topics_definitions_from(self, article, topics):
        result = []
        definitions = DifferenceBetween(article, topics).extractDefinitions()

        for topic in topics:
            for _def in definitions.values():
                if _def is None:
                    continue
                lower_def = _def.lower()

                if re.match(r"^((a)|(an) )?{} ((is)|(are)).+".format(topic), lower_def):
                    pos = util.topic_position(topic, lower_def)
                    if pos:
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
