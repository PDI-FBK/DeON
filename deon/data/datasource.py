import abc

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
    def pull(self, dest, download):
        """Pull the remote data and creates one (or more) TSV files locally.

        Arguments:
          dest: a path to a directory to be used for persistence.

        Returns:
          a file path.
        """
        pass
