from deon.data.datasource import DataSource
import deon.util as util
import os
import urllib.request
import tarfile


class WCLDataSource(DataSource):
    """
    NOTICE
    Get wiki_really_good and wiki_really_bad from this LINK: http://data.dws.informatik.uni-mannheim.de/dustalov/wcl/
    rename them into wiki_good and wiki_bad and substitute the existing ones
    """
    KEY = 'wcl'
    _LINK = 'http://lcl.uniroma1.it/wcl/wcl_datasets_v1.2.tar.gz'
    _OUT_DEF_FILE = 'wcl.def.tsv'
    _OUT_NODEF_FILE = 'wcl.nodef.tsv'
    _SOURCE_UKWAC = 'wcl_datasets_v1.2/ukwac/ukwac_estimated_recall.txt'
    _SOURCE_WIKI_GOOD = 'wcl_datasets_v1.2/wiki_good.txt'
    _SOURCE_WIKI_BAD = 'wcl_datasets_v1.2/wiki_bad.txt'

    def pull(self, dest, download):
        print('Pulling from wcl dataset...')
        if download:
            f_path = os.path.join(dest, 'wcl.tar.gz')
            with open(f_path, 'wb') as f_out:
                f_out.write(urllib.request.urlopen(self._LINK).read())
            with tarfile.open(f_path, 'r:gz') as targz:
                def is_within_directory(directory, target):
                    
                    abs_directory = os.path.abspath(directory)
                    abs_target = os.path.abspath(target)
                
                    prefix = os.path.commonprefix([abs_directory, abs_target])
                    
                    return prefix == abs_directory
                
                def safe_extract(tar, path=".", members=None, *, numeric_owner=False):
                
                    for member in tar.getmembers():
                        member_path = os.path.join(path, member.name)
                        if not is_within_directory(path, member_path):
                            raise Exception("Attempted Path Traversal in Tar File")
                
                    tar.extractall(path, members, numeric_owner=numeric_owner) 
                    
                
                safe_extract(targz, dest)

        if util.tsv_already_exist(dest, [self._OUT_DEF_FILE, self._OUT_NODEF_FILE]):
            return

        source_uwak = os.path.join(dest, self._SOURCE_UKWAC)
        source_good = os.path.join(dest, self._SOURCE_WIKI_GOOD)
        source_bad = os.path.join(dest, self._SOURCE_WIKI_BAD)

        sources = [(source_uwak, True), (source_good, True), (source_bad, False)]
        for source, _ in sources:
            assert os.path.exists(source)

        f_out_def_path = os.path.join(dest, self._OUT_DEF_FILE)
        f_out_nodef_path = os.path.join(dest, self._OUT_NODEF_FILE)
        for source, _def in sources:
            prevLine = ''
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
                phrase = ' '.join(util.tokenize(phrase))
                is_def = 1 if _def else 0
                if is_def == 1:
                    pos = util.topic_position(subject, phrase)
                    util.save_output(f_out_def_path, phrase, is_def, self.KEY, topic=subject, topic_pos=pos)
                else:
                    util.save_output(f_out_nodef_path, phrase, is_def, self.KEY, topic=subject)

        print('\tDONE\n')
        return
