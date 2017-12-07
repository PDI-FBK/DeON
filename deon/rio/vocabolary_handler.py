from deon.rio.vocabolary import Vocabolary
import deon.util as util
from pathlib import Path
import os


class VocabolaryHandler():

    def __init__(self, path_list, dest):
        self.path_list = path_list
        self.dest = dest

    def get_vocabolary(self):
        if self._vocabolary_path().exists():
            return self._load()
        return self._create(self.path_list)

    def _load(self):
        vocab_path = self._vocabolary_path()
        vocabolary = Vocabolary()
        for word in util.read_from(vocab_path):
            word = word.replace('\n', '')
            if word:
                vocabolary.add(word)
        return vocabolary

    def _create(self, f_inputs):
        vocab_path = self._vocabolary_path()
        vocabolary = Vocabolary()
        vocabolary.add('<EOS>')
        for f_input_path in f_inputs:
            for line in util.read_from(f_input_path):
                sentence, _ = line.split('\t')
                _ = [vocabolary.add(word) for word in sentence.split()]
        with open(vocab_path, 'w') as f:
            for _, word in vocabolary.items():
                f.write(word + '\n')
        return vocabolary

    def _vocabolary_path(self):
        vocab_path = os.path.join(self.dest, 'vocabolary.idx')
        return Path(vocab_path)

