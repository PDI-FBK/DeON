import tensorflow as tf
from pathlib import Path
import deon.util as util


class TrainExample():

    SENTENCE_LENGTH_KEY = 'sentence_length'
    DEF_LENGTH_KEY = 'definition_length'
    WORDS_KEY = 'words'
    DEF_KEY = 'definition'

    def encode(self, words_idxs, definition_idxs):
        example = tf.train.Example(
            features=tf.train.Features(
                feature={
                    self.SENTENCE_LENGTH_KEY: tf.train.Feature(
                        int64_list=tf.train.Int64List(
                            value=[len(words_idxs)])),
                    self.DEF_LENGTH_KEY: tf.train.Feature(
                        int64_list=tf.train.Int64List(
                            value=[len(definition_idxs)])),
                    self.WORDS_KEY: tf.train.Feature(
                        int64_list=tf.train.Int64List(
                            value=words_idxs)),
                    self.DEF_KEY: tf.train.Feature(
                        int64_list=tf.train.Int64List(
                            value=definition_idxs)),
                }
            )
        )
        return example

    def decode(self, example):

        def _parse_int(feature):
            return int(feature.int64_list.value[0])

        def _parse_int_list(feature):
            return [int(item) for item in feature.int64_list.value]

        fmap = example.features.feature
        _parse_int(fmap[self.SENTENCE_LENGTH_KEY])
        _parse_int(fmap[self.DEF_LENGTH_KEY])
        words = _parse_int_list(fmap[self.WORDS_KEY])
        formula = _parse_int_list(fmap[self.DEF_KEY])
        return words, formula


def generate_rio_dataset(ls_file_paths, vocabolary):
    print()
    train_example = TrainExample()
    for tsv_path in ls_file_paths:
        print('Saving rio file for:', tsv_path)
        rio_path = tsv_path + ".rio"
        if Path(rio_path).exists():
            continue
        with tf.python_io.TFRecordWriter(rio_path) as writer:
            for line in util.read_from(tsv_path):
                sentence, _def = line.split('\t')
                words = sentence.split()
                w_idx = [vocabolary.index(word) for word in words]
                writer.write(train_example.encode(w_idx, [int(_def)])
                    .SerializeToString())
    return
