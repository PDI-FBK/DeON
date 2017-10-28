from datasource import DataSource
import os
import urllib.request
import tarfile


class WCLDataSource(DataSource):
    KEY = 'wcl'
    _LINK = 'http://lcl.uniroma1.it/wcl/wcl_datasets_v1.2.tar.gz'
    _OUT_FILE = 'wcl.tsv'
    _SOURCE_UKWAC = 'wcl_datasets_v1.2/ukwac/ukwac_estimated_recall.txt'
    _SOURCE_WIKI_GOOD = 'wcl_datasets_v1.2/wikipedia/wiki_good.txt'
    _SOURCE_WIKI_BAD = 'wcl_datasets_v1.2/wikipedia/wiki_bad.txt'

    def pull(self, dest):
        print('Pulling for wcl dataset...')
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
                for i, line in enumerate(open(source)):
                    line = line.replace('\t', '')
                    line = line.strip('! #\n')
                    if not line:
                        continue
                    if i % 2 == 0:
                        prevLine = line
                        continue

                    subject, _ = line.split(':', maxsplit=1)
                    phrase = prevLine.replace('TARGET', subject)
                    out_line = '{}\t{}\t{}\n'\
                                .format(self.KEY, phrase, 1 if _def else 0)

                    f_out.write(out_line)

        return f_out_path
