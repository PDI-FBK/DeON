import os
from deon.rio.vocabolary_handler import VocabolaryHandler
from deon.rio.train_example import *
from deon.progressbar import Progressbar

class Splitter():

    def __init__(self):
        self.progressbar = Progressbar()

    def split_dataset(self, dataset_folder, split):
        split = list(split)
        data = self.count_dataset(dataset_folder, split)
        _max_nr_of_sentences = self.max_nr_of_sentences(data)
        nr_train, nr_test, nr_validation = self.get_total_by_percentage(_max_nr_of_sentences, split)

        train_file_path = self.create_dataset(dataset_folder, data, nr_train, 0)
        test_file_path = self.create_dataset(dataset_folder, data, nr_test, 1)
        validation_file_path = self.create_dataset(dataset_folder, data, nr_validation, 2)

        self.save_rio([train_file_path, test_file_path, validation_file_path], dataset_folder)

        return

    def save_rio(self, path_list, dataset_folder):
        vocabolary = VocabolaryHandler(path_list, dataset_folder).get_vocabolary()
        generate_rio_dataset(path_list, vocabolary)

    def create_dataset(self, folder, data, nr, pos):
        nr_def = nr // 2
        nr_nodef = nr_def
        filepath = os.path.join(folder, self.get_filename(pos))
        while nr_def > 0 or nr_nodef > 0:
            for _, info in data.items():
                self.progressbar.update()
                if nr_def > 0 and info['def_split'][pos] > 0:
                    _def = next(info['def_iter'])
                    nr_def -= 1
                    info['def_split'][pos] -= 1
                    self.save_to(_def, filepath)

                if nr_nodef > 0 and info['nodef_split'][pos] > 0:
                    _nodef = next(info['nodef_iter'])
                    nr_nodef -= 1
                    info['nodef_split'][pos] -= 1
                    self.save_to(_nodef, filepath)
        return filepath

    def save_to(self, line, filepath):
        sentence, _, _, _def, _ = line.split('\t')
        with open(filepath, 'a') as f:
            f.write('{} <EOS>\t{}\n'.format(sentence, _def))

    def get_filename(self, pos):
        if pos == 0:
            return 'train.tsv'
        if pos == 1:
            return 'test.tsv'
        if pos == 2:
            return 'validation.tsv'

    def get_total_by_percentage(self, nr, split):
        _train = 0
        _test = 0
        _validation = 0

        _train = int((split[0] / 100) * nr)
        if len(split) == 2:
            _test = int(nr - _train)
        elif len(split) == 3:
            _test = int((split[1]) / 100 * nr)
            _validation = int(nr - _train - _test)
        return [_train, _test, _validation]

    def count_lines(self, filepath):
        count = 0
        with open(filepath, 'r') as f:
            for line in f:
                count += 1
        return count

    def count_dataset(self, tmp, split):
        result = {}
        for filename in os.listdir(tmp):
            if not filename.endswith('.tsv'):
                continue
            filepath = os.path.join(tmp, filename)
            names = filename.split('.')
            _count_lines = self.count_lines(filepath)
            _split = self.get_total_by_percentage(_count_lines, split)

            if 'def' not in names and 'nodef' not in names:
                continue

            if names[0] not in result:
                result[names[0]] = {}
            if 'nodef' in names:
                result[names[0]]['nodef_count'] = _count_lines
                result[names[0]]['nodef_split'] = _split
                result[names[0]]['nodef_iter'] = self.read_from(filepath)
            elif 'def' in names:
                result[names[0]]['def_count'] = _count_lines
                result[names[0]]['def_split'] = _split
                result[names[0]]['def_iter'] = self.read_from(filepath)
        return result

    def max_nr_of_sentences(self, data):
        def_sum = 0
        nodef_sum = 0
        for _, value in data.items():
            def_sum += value['def_count']
            nodef_sum += value['nodef_count']
        return min(def_sum, nodef_sum)

    def read_from(self, filepath):
        with open(filepath, 'r') as f:
            for line in f:
                yield line
