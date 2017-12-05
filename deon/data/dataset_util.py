import os


def split_dataset(dataset_folder, split):
    split = list(split)
    print('split dataset')
    data = count_dataset(dataset_folder)
    max_nr_of_senteces = max_nr_of_sentences(data)
    nr_train, nr_test, nr_validation = get_total_by_percentage(max_nr_of_senteces, split)
    ordered_files = zip_ordered_def_nodef_files(data, split)

    create_dataset(dataset_folder, ordered_files, nr_train, 0)
    create_dataset(dataset_folder, ordered_files, nr_test, 1)
    create_dataset(dataset_folder, ordered_files, nr_validation, 2)

    return


def create_dataset(dataset_folder, ordered_files, nr, pos):
    print("-----------")
    dest_path = os.path.join(dataset_folder, get_filename(pos))
    print(dest_path)
    count = 0
    def_c = 0
    nodef_c = 0
    with open(dest_path, 'w') as f:
        while count < nr:
            for file_iter, counters in ordered_files:
                if counters[pos] <= 0:
                    continue
                counters[pos] -= 1
                sentence, _, _, _def, _ = next(file_iter).split('\t')
                if _def == '1':
                    def_c += 1
                else:
                    nodef_c += 1
                # f.write('{} <EOS>\t{}\n'.format(sentence, _def))
                count += 1
                if count == nr:
                    break
    print(def_c, nodef_c)


def get_filename(pos):
    if pos == 0:
        return 'train.tsv'
    if pos == 1:
        return 'test.tsv'
    if pos == 2:
        return 'validation.tsv'


def zip_ordered_def_nodef_files(data, split):
    ordered_def_files = [(read_from(filepath), get_total_by_percentage(data['def'][filepath], split))
                        for filepath in sort(data['def'])]
    ordered_nodef_files = [(read_from(filepath), get_total_by_percentage(data['nodef'][filepath], split))
                        for filepath in sort(data['nodef'])]
    ordered_files = [item for sublist in zip(ordered_def_files, ordered_nodef_files) for item in sublist]
    return ordered_files


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


def count_dataset(tmp):
    result = {'def': {}, 'nodef': {}}
    for filename in os.listdir(tmp):
        if not filename.endswith('.tsv'):
            continue
        filepath = os.path.join(tmp, filename)
        names = filename.split('.')
        if 'w00' in names or 'msresearch' in names:
            if 'nodef' in names:
                result['nodef'][filepath] = count_lines(filepath)
            elif 'def' in names:
                result['def'][filepath] = count_lines(filepath)
    return result


def max_nr_of_sentences(data):
    def_sum = 0
    nodef_sum = 0
    for vl in data['def'].values():
        def_sum += vl
    for vl in data['nodef'].values():
        nodef_sum += vl
    return min(def_sum, nodef_sum)


def sort(data):
    return sorted(data, key=data.get)


def read_from(filepath):
    with open(filepath, 'r') as f:
        for line in f:
            yield line
