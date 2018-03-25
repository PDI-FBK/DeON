from deon.data.datasource import DataSource
from deon.data.txt_classifier import TxtClassifier
import os
import json
import deon.util as util


class WikipediaSource(DataSource):
    """DataSource implementation for the w00 dataset."""

    KEY = 'wikipedia'
    _INPUT_FOLDER = 'wikipedia'
    _OUT_FILES = ['wikipedia.def.tsv', 'wikipedia.nodef.tsv', 'wikipedia.anafora.tsv']

    MAX_NODEF = 600000

    def pull(self, dest, download):
        print('Pulling from wikipedia dataset...\n')

        if util.tsv_already_exist(dest, self._OUT_FILES):
            return

        self.dest = dest
        wiki_folder = os.path.join(dest, self._INPUT_FOLDER)
        classifier = TxtClassifier()

        content_folders = os.listdir(wiki_folder)
        for i, folder in enumerate(content_folders):
            content_folder_path = os.path.join(wiki_folder, folder)
            content_files = os.listdir(content_folder_path)
            for j, file_name in enumerate(content_files):
                progress = '{} [{}/{}]'.format(i, j, len(content_files))
                util.print_progress('Extracting def/nodef ', progress, len(content_folders))
                file = os.path.join(content_folder_path, file_name)
                self._parse(file, classifier)
        return

    def _parse(self, file, classifier):
        with open(file, 'r') as f:
            for line in f:
                line = json.loads(line)
                topic = line['title']
                content = line['text']
                url = line['url']

                if not topic[0].isalnum() or topic[0] == '?':
                    continue

                for c, t, s in classifier.classify(content, set([topic])):
                    pos = util.topic_position(t, s)
                    if not pos:
                        pos = '?'
                    if c == 'def':
                        self._save_def(s, url, t, pos)
                    if c == 'nodef':
                        self._save_nodef(s, url, t, pos)
                    if c == 'anafora':
                        self._save_anafora(s, url)
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
