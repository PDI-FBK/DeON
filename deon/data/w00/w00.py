from datasource import DataSource
import os
import urllib.request
import zipfile


class W00DataSource(DataSource):
    """DataSource implementation for the w00 dataset."""

    KEY = 'w00'
    _LINK = 'https://github.com/YipingNUS/DefMiner/raw/master/W00_dataset.zip'
    _SOURCE_WORD = 'W00_dataset/annotated.word'
    _SOURCE_META = 'W00_dataset/annotated.word'
    _OUT_FILE = 'w00.tsv'

    def pull(self, dest):
        print('Pulling for w00 dataset...')
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
