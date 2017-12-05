import os


def split_dataset(dataset_folder, split):
    split = list(split)
    data = count_dataset(dataset_folder, split)
    _max_nr_of_sentences = max_nr_of_sentences(data)
    nr_train, nr_test, nr_validation = get_total_by_percentage(_max_nr_of_sentences, split)

    create_dataset(dataset_folder, data, nr_train, 0)
    create_dataset(dataset_folder, data, nr_test, 1)
    create_dataset(dataset_folder, data, nr_validation, 2)

    return


def create_dataset(folder, data, nr, pos):
    nr_def = nr // 2
    nr_nodef = nr_def
    filepath = os.path.join(folder, get_filename(pos))
    while nr_def > 0 or nr_nodef > 0:
        for _, info in data.items():
            if nr_def > 0 and info['def_split'][pos] > 0:
                _def = next(info['def_iter'])
                nr_def -= 1
                info['def_split'][pos] -= 1
                save_to(_def, filepath)

            if nr_nodef > 0 and info['nodef_split'][pos] > 0:
                _nodef = next(info['nodef_iter'])
                nr_nodef -= 1
                info['nodef_split'][pos] -= 1
                save_to(_nodef, filepath)
    return


def save_to(line, filepath):
    sentence, _, _, _def, _ = line.split('\t')
    with open(filepath, 'a') as f:
        f.write('{} <EOS>\t{}\n'.format(sentence, _def))


def get_next(info, pos):
    _def = None
    _nodef = None
    if info['def_split'][pos] > 0:
        _def = next(info['def_iter'])
    if info['nodef_split'][pos] > 0:
        _def = next(info['nodef_iter'])
    return _def, _nodef


def get_filename(pos):
    if pos == 0:
        return 'train.tsv'
    if pos == 1:
        return 'test.tsv'
    if pos == 2:
        return 'validation.tsv'


def get_total_by_percentage(nr, split):
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


def count_lines(filepath):
    count = 0
    with open(filepath, 'r') as f:
        for line in f:
            count += 1
    return count


def count_dataset(tmp, split):
    result = {}
    for filename in os.listdir(tmp):
        if not filename.endswith('.tsv'):
            continue
        filepath = os.path.join(tmp, filename)
        names = filename.split('.')
        _count_lines = count_lines(filepath)
        _split = get_total_by_percentage(_count_lines, split)
        if names[0] not in result:
            result[names[0]] = {}
        if 'nodef' in names:
            result[names[0]]['nodef_count'] = _count_lines
            result[names[0]]['nodef_split'] = _split
            result[names[0]]['nodef_iter'] = read_from(filepath)
        elif 'def' in names:
            result[names[0]]['def_count'] = _count_lines
            result[names[0]]['def_split'] = _split
            result[names[0]]['def_iter'] = read_from(filepath)
    return result


def max_nr_of_sentences(data):
    def_sum = 0
    nodef_sum = 0
    for _, value in data.items():
        def_sum += value['def_count']
        nodef_sum += value['nodef_count']
    return min(def_sum, nodef_sum)


def read_from(filepath):
    with open(filepath, 'r') as f:
        for line in f:
            yield line
