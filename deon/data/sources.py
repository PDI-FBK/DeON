"""Data sources management."""

import abc
import os
import zipfile
import urllib.request
import tarfile

def resolve(key):
    """Resolve the DataSource by its key."""
    if key == W00DataSource.KEY:
        return W00DataSource()
    elif key == MsResearchSource.KEY:
        return MsResearchSource()
    elif key == WCLDataSource.KEY:
        return WCLDataSource() 

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

class MsResearchSource(DataSource):
    KEY = 'msresearch'
    _LINK = 'http://taln.upf.edu/web_old/system/files/resources_files/ms_research_defs-nodefs.txt'
    _OUT_FILE = 'msresearch.tsv'

    def pull(self, dest):
        f_path = os.path.join(dest, 'msresearch.txt')
        with open(f_path, 'wb') as f_out:
            f_out.write(urllib.request.urlopen(self._LINK).read())

        source = open(f_path)
        f_out_path = os.path.join(dest, self._OUT_FILE)
        with open(f_out_path, 'w') as f_out:
            for line in source:
                line = line.strip()
                if not line:
                    continue

                is_def, phrase = line.split('/', 1)
                def_flag = is_def == 'DEF'
                out_line = "{}\t{}\t{}\n"\
                            .format(self.KEY, phrase, 1 if def_flag else 0)
                f_out.write(out_line)

        return f_out_path

class WCLDataSource(DataSource):
    KEY = 'wcl'
    _LINK = 'http://lcl.uniroma1.it/wcl/wcl_datasets_v1.2.tar.gz'
    _OUT_FILE = 'wcl.tsv'
    _SOURCE_UKWAC = 'wcl_datasets_v1.2/ukwac/ukwac_estimated_recall.txt'
    _SOURCE_WIKI_GOOD = 'wcl_datasets_v1.2/wikipedia/wiki_good.txt'
    _SOURCE_WIKI_BAD = 'wcl_datasets_v1.2/wikipedia/wiki_bad.txt'

    def pull(self, dest):
        f_path = os.path.join(dest, 'wcl.tar.gz')
        with open(f_path, 'wb') as f_out:
            f_out.write(urllib.request.urlopen(self._LINK).read())
        with tarfile.open(f_path, 'r:gz') as targz:
            targz.extractall(dest)

        source_uwak = os.path.join(dest, self._SOURCE_UKWAC)
        source_good = os.path.join(dest, self._SOURCE_WIKI_GOOD)
        source_bad = os.path.join(dest, self._SOURCE_WIKI_BAD)

        sources = [(source_uwak, True), (source_good, True), (source_bad, False)]
        for source, _ in sources:
            assert os.path.exists(source)

        f_out_path = os.path.join(dest, self._OUT_FILE)
        for source, _def in sources:
            prevLine = ''
            with open(f_out_path, 'a') as f_out:
                for i,line in enumerate(open(source)):
                    line = line.replace('\t', '')
                    line = line.strip('! #\n')
                    if not line:
                        continue
                    if i%2 == 0:
                        prevLine = line
                        continue

                    subject, _ = line.split(':', maxsplit=1)
                    phrase = prevLine.replace('TARGET', subject)
                    out_line = '{}\t{}\t{}\n'\
                                .format(self.KEY, phrase, 1 if _def else 0)

                    f_out.write(out_line)

        return f_out_path
