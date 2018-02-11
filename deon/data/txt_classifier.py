from nltk.tokenize import sent_tokenize
import deon.util as util
from deon.data.np_extractor import NPExtractor
import re


class TxtClassifier():

    def __init__(self):
        self.wcl_process = util.start_wcl_process()

    def classify(self, txt, topics):
        sentences = sent_tokenize(txt)
        for sentence in sentences:
            if self._ignore(sentence):
                continue
            extract_topics = NPExtractor(sentence).extract()
            _topics = list(set(topics).union(set(extract_topics)))
            _topics = [x for x in _topics if len(x.split()) < 5]
            if len(_topics) == 0:
                continue
            is_classified = False
            for topic in _topics:
                if not topic.isalnum():
                    continue
                classifier = self._classify(sentence, topic)
                if not classifier:
                    continue
                sentence = ' '.join(util.tokenize(sentence))
                yield classifier, topic, sentence
                is_classified = True
                break
            if not is_classified and self._is_no_def(sentence):
                topic = _topics[0]
                if _topics[0] in sentence:
                    topic = _topics[0]
                elif len(_topics) > 1:
                    topic = _topics[1]
                sentence = ' '.join(util.tokenize(sentence))
                yield 'nodef', topic, sentence

    def _ignore(self, sentence):
        return len(sentence.split()) > 300 or\
            sentence.strip().endswith('?') or\
            'Lookout' in sentence or\
            'Public Domain' in sentence or\
            len(sentence.split(',')) > 6 or\
            re.search('[0-9]+ \w+ [0-9]+', sentence) is not None

    def _classify(self, sentence, topic):
        _sentence = ' '.join(util.tokenize(sentence.lower()))
        _topic = topic.lower()
        if self._is_anafora(_sentence):
            return 'anafora'
        if self._is_def(_sentence, _topic):
            return 'def'
        return

    def _is_def(self, sentence, topic):
        if not sentence[0].isalpha():
            return False
        return util.query_wcl_for(self.wcl_process, topic, sentence)

    def _is_anafora(self, sentence):
        blacklist = set(['he', 'she', 'it', 'this', 'these', 'they', 'their', 'her', 'his', 'its', 'hers'])
        ls = set(sentence.split())
        return len(blacklist.intersection(ls)) > 0

    def _is_no_def(self, sentence):
        return not self._is_in_blacklist(sentence)

    def _is_in_blacklist(self, sentence):
        blacklist = ['therefore', 'although', 'however', 'another']
        ls = sentence.split()
        return ls[0] in blacklist

    def _extract_subtopics(self, topic):
        topic = topic.lower()
        return topic.split()

    def _is_fully_related_with_topic(self, sentence, topic):
        return topic in sentence

    def _is_edge_case(self, ch):
        return ch == '?'
