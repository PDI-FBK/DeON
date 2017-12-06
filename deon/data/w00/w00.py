from deon.data.datasource import DataSource
import deon.util as util
import os
import urllib.request
import zipfile


class W00DataSource(DataSource):
    """DataSource implementation for the w00 dataset."""

    KEY = 'w00'
    _LINK = 'https://github.com/YipingNUS/DefMiner/raw/master/W00_dataset.zip'
    _SOURCE_WORD = 'W00_dataset/annotated.word'
    _SOURCE_META = 'W00_dataset/annotated.meta'
    _OUT_DEF_FILE = 'w00.def.tsv'
    _OUT_NODEF_FILE = 'w00.nodef.tsv'

    def pull(self, dest, download):
        print('Pulling from w00 dataset...')
        if download:
            f_path = os.path.join(dest, 'w00.zip')
            with open(f_path, 'wb') as f_out:
                f_out.write(urllib.request.urlopen(self._LINK).read())
            with zipfile.ZipFile(f_path) as zipf:
                zipf.extractall(dest)

        if util.tsv_already_exist(dest, [self._OUT_DEF_FILE, self._OUT_NODEF_FILE]):
            return

        source_word = os.path.join(dest, self._SOURCE_WORD)
        source_meta = os.path.join(dest, self._SOURCE_META)
        assert os.path.exists(source_word)
        assert os.path.exists(source_meta)

        f_out_def_path = os.path.join(dest, self._OUT_DEF_FILE)
        f_out_nodef_path = os.path.join(dest, self._OUT_NODEF_FILE)
        for line, meta in zip(open(source_word), open(source_meta)):
            line = line.strip()
            if not line:
                continue
            line = ' '.join(util.tokenize(line))
            def_flag = 1 if meta.startswith('1') else 0
            if def_flag == 1:
                util.save_output(f_out_def_path, line, def_flag, self.KEY)
            else:
                util.save_output(f_out_nodef_path, line, def_flag, self.KEY)

        print('\tDONE\n')
        return
