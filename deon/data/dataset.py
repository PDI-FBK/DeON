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


def build(source_keys=('w00',), dest='dataset', split=(80, 20), tmp=None, force=False):
    """Build the DeON dataset from differnt data sources."""

    dest = _dest_dir(dest, force)
    tmp = _tmp_dir(tmp, force)

    for f_path in [sources.resolve(key).pull(tmp) for key in source_keys]:
        shutil.move(f_path, dest)

    # TODO: implement everything else.

    # tmp directory cleanup
    shutil.rmtree(tmp)
