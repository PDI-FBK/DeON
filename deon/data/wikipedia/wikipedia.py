from deon.data.datasource import DataSource
import os
import re
import json
import deon.data.util as util


class WikipediaSource(DataSource):
    """DataSource implementation for the w00 dataset."""

    KEY = 'wikipedia'
    _INPUT_FOLDER = 'wikipedia'
    _OUT_FILES = ['wikipedia.def.tsv', 'wikipedia.nodef.tsv', 'wikipedia.anafora.tsv']

    def pull(self, dest, download):
        print('Pulling from wikipedia dataset...\n')
        self.dest = dest
        wiki_folder = os.path.join(dest, self._INPUT_FOLDER)
        wcl_process = util.start_wcl_process()
        f_out_path = os.path.join(dest, self._OUT_FILES[0])

        content_folders = os.listdir(wiki_folder)
        for i, folder in enumerate(content_folders):
            content_folder_path = os.path.join(wiki_folder, folder)
            content_files = os.listdir(content_folder_path)
            for j, file_name in enumerate(content_files):
                progress = '{} [{}/{}]'.format(i, j, len(content_files))
                util.print_progress('Extracting def/nodef ', progress, len(content_folders))
                file = os.path.join(content_folder_path, file_name)
                self._parse(file, wcl_process)
        return f_out_path

    def _parse(self, file, wcl_process):
        with open(file, 'r') as f:
            for line in f:
                line = json.loads(line)
                topic = line['title']
                content = line['text']
                url = line['url']
                subtopics = self._extract_subtopics(topic)
                for sentence in self._split_to_sentecens(content):
                    _sentence = sentence.lower()
                    if not self._is_long_enough_sentence(_sentence):
                        continue
                    if not topic[0].isalnum():
                        continue
                    if self._is_edge_case(topic[0]):
                        continue

                    if self._is_anafora(_sentence):
                        self._save_anafora(sentence, url)

                    elif not self._is_related_to_topic(_sentence, subtopics):
                        self._save_nodef(sentence, url)

                    elif self._is_fully_related_with_topic(_sentence, topic):
                        _def = util.query_wcl_for(wcl_process, topic.lower(), _sentence)
                        pos = util.topic_position(topic.lower(), _sentence)
                        if _def:
                            self._save_def(sentence, url, topic.lower(), pos)
                        else:
                            self._save_nodef(sentence, url, topic.lower(), pos)
        return

    def _save_def(self, sentence, url, topic, pos):
        out_file = os.path.join(self.dest, self._OUT_FILES[0])
        util.save_output(out_file, sentence, '1', url, topic, pos)

    def _save_nodef(self, sentence, url, topic='?', pos='?'):
        out_file = os.path.join(self.dest, self._OUT_FILES[1])
        util.save_output(out_file, sentence, '0', url, topic, pos)

    def _save_anafora(self, sentence, url):
        out_file = os.path.join(self.dest, self._OUT_FILES[2])
        util.save_output(out_file, sentence, '0', url, '?', '?')

    def _is_long_enough_sentence(self, sentence):
        ls = set(sentence.split())
        return len(ls) > 5

    def _is_in_blacklist(self, sentence):
        blacklist = ['therefore', 'although', 'however', 'another']
        ls = sentence.split()
        return ls[0] in blacklist

    def _is_anafora(self, sentence):
        blacklist = ['he', 'she', 'it', 'this', 'these', 'they', 'her', 'his', 'its']
        ls = sentence.split()
        return ls[0] in blacklist

    def _is_related_to_topic(self, sentence, topics):
        for topic in topics:
            if topic in sentence:
                return True
        return False

    def _is_fully_related_with_topic(self, sentence, topic):
        return topic in sentence

    def _split_to_sentecens(self, txt):
        txt = txt.replace('.\n\n', ' .# ')
        txt = txt.replace('? ', ' ?# ')
        txt = txt.replace('! ', ' !# ')
        txt = txt.replace('. ', ' .# ')
        txt = txt.replace('(', '( ')
        txt = txt.replace(')', ' ) ')
        txt = txt.replace('"', ' " ')
        txt = txt.replace('\n\n', ' .# ')
        txt = txt.replace('\n', ' ')
        txt = txt.replace(',', ' , ')
        sentences = re.split('#+ ', txt)
        return [' '.join(s.split()) for s in sentences]

    def _extract_subtopics(self, topic):
        topic = topic.lower()
        return [topic] + topic.split()

    def _is_edge_case(self, ch):
        return ch == '?'
