"""DeON dataset management utilities."""

import os
import tempfile
import shutil

import deon.data.sources as sources


def build(source_keys=('w00'), dest='dataset', split=(80, 20), seed=23, tmp=None, force=False):
    """Build the DeON dataset from differnt data sources."""

    if os.path.exists(dest):
        if force:
            shutil.rmtree(dest)
        else:
            raise IOError('The destination directory {} already exists.', dest)

    if not tmp:
        tmp = tempfile.mkdtemp()

    f_paths = [sources.resolve(key).pull(tmp) for key in source_keys]
    
    # TODO: implement everything else.
