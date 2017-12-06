"""DeON dataset management utilities."""

import os
import shutil
import tempfile

import deon.data.sources as sources
import deon.data.dataset_util as dataset_util

def _tmp_dir(tmp, force):
    if not tmp:
        return tempfile.mkdtemp()

    if os.path.exists(tmp):
        files = os.listdir(tmp)
        if files and force:
            shutil.rmtree(tmp)
            os.makedirs(tmp)
    else:
        os.makedirs(tmp)

    return tmp


def _dest_dir(dest, force):
    if os.path.exists(dest):
        if force:
            shutil.rmtree(dest)
    else:
        os.makedirs(dest)
    return dest


def build(source_keys=('w00',), dest='dataset', split=(70, 20, 10), tmp=None, force=False, download=False):
    """Build the DeON dataset from differnt data sources."""
    # print("Build the DeON dataset from differnt data sources.")
    # dest = _dest_dir(dest, force)
    # tmp = _tmp_dir(tmp, force)
    # [sources.resolve(key).pull(tmp, download) for key in source_keys]
    print('Splitting dataset', split, '...')
    dataset_util.split_dataset(tmp, split)
    print('Done!')
