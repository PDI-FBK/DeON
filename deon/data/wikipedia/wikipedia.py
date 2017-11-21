from deon.data.datasource import DataSource

class WikipediaDataSource(DataSource):
    """DataSource implementation for the w00 dataset."""

    KEY = 'wikipedia'
    _PAGE_FOLDER = 'wikipedia'
    _OUT_FILES = ['wikipedia.def.tsv', 'wikipedia.nodef.tsv', 'wikipedia.anafora.tsv', 'wikipedia.wcl.tsv']

    def pull(self, dest, download):
        print('Pulling from wikipedia dataset...')
        return
