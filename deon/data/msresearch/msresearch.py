from datasource import DataSource
import os
import urllib.request


class MsResearchSource(DataSource):
    KEY = 'msresearch'
    _LINK = 'http://taln.upf.edu/web_old/system/files/resources_files/ms_research_defs-nodefs.txt'
    _OUT_FILE = 'msresearch.tsv'

    def pull(self, dest):
        print('Pulling for msresearch dataset...')
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
