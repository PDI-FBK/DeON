"""DeON dataset management utilities."""

import os
import shutil
import tempfile

import deon.data.sources as sources


def _tmp_dir(tmp, force):
    if not tmp:
        return tempfile.mkdtemp()

    if os.path.exists(tmp):
        files = os.listdir(tmp)
        if files and not force:
            raise IOError(
                'The selected temp directory `{}` already exists and is not empty.'\
                    .format(tmp))
        shutil.rmtree(tmp)
    os.makedirs(tmp)
    return tmp


def _dest_dir(dest, force):
    if os.path.exists(dest):
        if force:
            shutil.rmtree(dest)
        else:
            raise IOError('The destination directory {} already exists.', dest)
    os.makedirs(dest)
    return dest

def _get_split_index(_len, split):
    res = []
    for s in split:
        s /= 100
        if len(res) == 0:
            res.append((0, int(_len*s)))
            continue
        res.append( (res[-1][1], int(_len*s) + res[-1][1]) )
    return res

def _split(dataset_file, split, destination):
    source = ['training.tsv', 'validation.tsv', 'testing.tsv']
    defs = []
    nodefs = []
    with open(dataset_file, 'r') as f:
        for line in f:
            _, _, _def = line.split('\t')
            if int(_def) == 1:
                defs.append(line)
            else:
                nodefs.append(line)

    def_split_indexes = _get_split_index(len(defs), split)
    print(def_split_indexes)
    print("defs", len(defs))
    nodef_split_indexes = _get_split_index(len(nodefs), split)
    print(nodef_split_indexes)
    print("nodefs", len(nodefs))

    splitted_defs = [defs[i:j] for i,j in def_split_indexes]
    splitted_nodefs = [nodefs[i:j] for i,j in nodef_split_indexes]

    print([len(x) for x in splitted_defs])
    print([len(x) for x in splitted_nodefs])

    for i in range(len(split)):
        res = splitted_defs[i] + splitted_nodefs[i]
        source_path = destination + '/' + source[i]
        print(source_path)
        with open(source_path, 'w') as source_file:
            for data in res:
                source_file.write(data)
    



def build(source_keys=('w00',), dest='dataset', split=(80, 20), tmp=None, force=False):
    """Build the DeON dataset from differnt data sources."""

    dest = _dest_dir(dest, force)
    tmp = _tmp_dir(tmp, force)
    dataset_file = tmp + '/dataset.tsv'
    line_index = 0
    do_split = len(split) > 1

    for f_path in [sources.resolve(key).pull(tmp) for key in source_keys]:
        with open(dataset_file, 'a') as df:
            with open(f_path, 'r') as f:
                for line in f:
                    line_index += 1
                    line = '{}\t{}'.format(line_index, line)

                    df.write(line)


    if do_split:
        _split(f_path, split, dest)
    else:
        shutil.move(f_path, dest)

    # TODO: implement everything else.

    # tmp directory cleanup
    shutil.rmtree(tmp)
