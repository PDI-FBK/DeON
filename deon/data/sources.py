"""Data sources management."""
from deon.data.w00.w00 import W00DataSource
from deon.data.msresearch.msresearch import MsResearchSource
from deon.data.wcldata.wcldata import WCLDataSource
from deon.data.diffbetween.difference_between import DiffBetweenDataSource
from deon.data.dictionary.dictionary import DictionarySource
from deon.data.wikipedia.wikipedia import WikipediaSource


def resolve(key):
    """Resolve the DataSource by its key."""
    if key == W00DataSource.KEY:
        return W00DataSource()
    elif key == MsResearchSource.KEY:
        return MsResearchSource()
    elif key == WCLDataSource.KEY:
        return WCLDataSource()
    elif key == DiffBetweenDataSource.KEY:
        return DiffBetweenDataSource()
    elif key == DictionarySource.KEY:
        return DictionarySource()
    elif key == WikipediaSource.KEY:
        return WikipediaSource()

    raise KeyError('Invalid key: `{}`'.format(key))
