from deon.data.datasource import DataSource
from deon.data.txt_classifier import TxtClassifier
import os
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
        classifier = TxtClassifier()
        f_out_path = os.path.join(dest, self._OUT_FILES[0])

        content_folders = os.listdir(wiki_folder)
        for i, folder in enumerate(content_folders):
            content_folder_path = os.path.join(wiki_folder, folder)
            content_files = os.listdir(content_folder_path)
            for j, file_name in enumerate(content_files):
                progress = '{} [{}/{}]'.format(i, j, len(content_files))
                util.print_progress('Extracting def/nodef ', progress, len(content_folders))
                file = os.path.join(content_folder_path, file_name)
                self._parse(file, classifier)
        return f_out_path

    def _parse(self, file, classifier):
        with open(file, 'r') as f:
            for line in f:
                line = json.loads(line)
                topic = line['title']
                content = line['text']
                url = line['url']

                if not topic[0].isalnum() or topic[0] == '?':
                    continue

                classifier_result = classifier.classify(content, topic)
                for sentence in classifier_result['def']:
                    pos = util.topic_position(topic, sentence)
                    self._save_def(sentence, url, topic, pos)
                for sentence in classifier_result['nodef']:
                    pos = util.topic_position(topic, sentence)
                    _topic = topic
                    if not pos:
                        pos = '?'
                        _topic = '?'
                    self._save_nodef(sentence, url, _topic, pos)
                for sentence in classifier_result['anafora']:
                    pos = util.topic_position(topic, sentence)
                    self._save_anafora(sentence, url)
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
