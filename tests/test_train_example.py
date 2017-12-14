import unittest
from deon.rio.train_example import TrainExample


class TestEncodeDecode(unittest.TestCase):

    def test_encode_decode(self):
        train_example = TrainExample()
        _words = [2, 3, 4, 5, 6]
        _def = [0]

        example = train_example.encode(_words, _def)
        decoded_words, decoded_def = train_example.decode(example)

        self.assertEqual(_words, decoded_words)
        self.assertEqual(_def, decoded_def)

