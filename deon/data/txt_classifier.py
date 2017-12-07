from nltk.tokenize import sent_tokenize
import deon.util as util


class TxtClassifier():

    def __init__(self):
        self.wcl_process = util.start_wcl_process()

    def classify(self, txt, topic):
        result = {'def': set(), 'nodef': set(), 'anafora': set()}

        if not topic.isalnum():
            return result

        for sentence in sent_tokenize(txt):
            classifier = self._classify(sentence, topic)
            if not classifier:
                continue
            sentence = ' '.join(util.tokenize(sentence))
            result[classifier].add(sentence)
        return result

    def _classify(self, sentence, topic):
        _sentence = ' '.join(util.tokenize(sentence.lower()))
        _topic = topic.lower()
        if self._is_anafora(_sentence):
            return 'anafora'
        if self._is_def(_sentence, _topic):
            return 'def'
        if self._is_no_def(_sentence, _topic):
            return 'nodef'
        return

    def _is_def(self, sentence, topic):
        if not sentence[0].isalpha():
            return False
        return util.query_wcl_for(self.wcl_process, topic, sentence)

    def _is_anafora(self, sentence):
        blacklist = ['he', 'she', 'it', 'this', 'these', 'they', 'their', 'her', 'his', 'its', 'you']
        ls = sentence.split()
        return ls[0] in blacklist

    def _is_no_def(self, sentence, topic):
        if self._is_fully_realted_to_topic(sentence, topic):
            return True
        return not self._is_in_blacklist(sentence) and\
               not self._is_related_to_topic(sentence, topic)

    def _is_related_to_topic(self, sentence, topic):
        words = set(sentence.split())
        for top in self._extract_subtopics(topic):
            if top in words:
                return True
        return False

    def _is_fully_realted_to_topic(self, sentence, topic):
        return topic in sentence

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
