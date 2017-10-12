"""Data sources management."""

import abc
import os
import zipfile
import urllib.request


def resolve(key):
    """Resolve the DataSource by its key."""
    if key == W00DataSource.KEY:
        return W00DataSource()
    raise KeyError('Invalid key: `{}`'.format(key))


class DataSource(object):
    """Manages a remote data source.

    A remote data source is an external dataset that is exploited to create the
    DeON datasets. The DataSource class encapsulates the logic that is needed to
    download and properly format the data. Such logics must be implemented in
    (concrete) subclasses. Each DataSource object has a `KEY` attribute that
    identifies it.
    """

    __meta__ = abc.ABCMeta

    KEY = ''

    def __init__(self):
        """Initialize a DataSource object."""
        pass

    def key(self):
        """The current DataSource key."""
        return self.KEY

    @abc.abstractmethod
    def pull(self, dest):
        """Pull the remote data and creates one (or more) TSV files locally.
        
        Arguments:
          dest: a path to a directory to be used for persistence.
        
        Returns:
          a file path.
        """
        pass


class W00DataSource(DataSource):
    """DataSource implementation for the w00 dataset."""

    KEY = 'w00'
    _LINK = 'https://github.com/YipingNUS/DefMiner/raw/master/W00_dataset.zip'
    _SOURCE_WORD = 'W00_dataset/annotated.word'
    _SOURCE_META = 'W00_dataset/annotated.word'
    _OUT_FILE = 'w00.tsv'

    def pull(self, dest):
        f_path = os.path.join(dest, 'w00.zip')
        with open(f_path, 'wb') as f_out:
            f_out.write(urllib.request.urlopen(self._LINK).read())
        with zipfile.ZipFile(f_path) as zipf:
            zipf.extractall(dest)

        source_word = os.path.join(dest, self._SOURCE_WORD)
        source_meta = os.path.join(dest, self._SOURCE_META)
        assert os.path.exists(source_word)
        assert os.path.exists(source_meta)

        f_out_path = os.path.join(dest, self._OUT_FILE)
        with open(f_out_path, 'w') as f_out:
            for line, meta in zip(open(source_word), open(source_meta)):
                line = line.strip()
                if not line:
                    continue

                def_flag = 1 if meta.startswith('1') else 0
                out_line = '{}\t{}\t{}\n'.format(self.KEY, line, def_flag)
                f_out.write(out_line)

        return f_out_path
