import re

BLACKLIST = ['therefore', 'posted on', 'difference', 'help us', 'although',
            'those', 'CC', 'facebook', 'however', 'accessed',
            'structural formulae']
ANAFORA_BLACKLIST = ['he', 'she', 'it', 'this', 'these', 'they', 'her', 'his', 'its']


class NoDefinitions():
    def __init__(self, article, topics):
        self.sentences = self._get_sentences(article)
        self.topics = set(topics)

    def extract_no_def(self):
        nodef_ls = []

        for sentence in self.sentences:
            _sentence = set(sentence.lower().replace(',', ' ').split())
            _topics = self._split_topics()

            if _topics.intersection(_sentence):
                continue

            if len(_sentence) < 4:
                continue

            sentence = re.sub('[^\w,.\' /\\()-]', '', sentence).strip()
            if self._is_in_blacklist(sentence):
                continue
            if self._ends_with_punctuation(sentence):
                nodef_ls.append(sentence)
        return nodef_ls

    def extract_no_def_properties(self, set_defs):
        ls = []
        for sentence in self.sentences:
            _sentence = set(sentence.lower().replace(',', ' ').split())

            for topic in self.topics:
                if topic not in sentence.lower():
                    continue
                if not re.findall(r'(?:^|\s)'+ topic +'(?:\s|$)', sentence.lower()):
                    continue
                if len(_sentence) <= len(topic.split()):
                    continue
                if sentence in set_defs:
                    continue
                sentence = re.sub('[^\w,.\' /\\()-]', '', sentence).strip()
                if sentence in set_defs:
                    continue
                if self._ends_with_punctuation(sentence):
                    ls.append((sentence, topic))
        return ls

    def extract_anafora(self):
        ls = []
        for sentence in self.sentences:
            sentence = re.sub('[^\w,.\' /\\()-]', '', sentence).strip()
            if self._is_anafora(sentence):
                ls.append(sentence)
        return ls

    def _ends_with_punctuation(self, sentence):
        return re.match('^[A-Z][^?!.]*[?.!]$', sentence)

    def _extract_text(self, article):
        ps = [p.get_text() for p in article.find_all('p') if not p.strong]
        article_txt = ' '.join(ps)
        article_txt = ' '.join(article_txt.split())
        return article_txt

    def _split_to_sentecens(self, txt):
        txt = txt.replace('? ', '?# ')
        txt = txt.replace('! ', '!# ')
        txt = txt.replace(': ', ':# ')
        txt = txt.replace('. ', '.# ')
        txt = txt.replace(', ', ' , ')
        sentences = re.split('#+ ', txt)
        return [' '.join(s.split()) for s in sentences]

    def _get_sentences(self, article):
        article_txt = self._extract_text(article)
        return self._split_to_sentecens(article_txt)

    def _is_in_blacklist(self, sentence):
        ls = sentence.lower().replace(',', '').split()
        return self._is_anafora(sentence) or ls[0] in BLACKLIST

    def _split_topics(self):
        topics = [top.split() for top in self.topics]
        return set([item for sublist in topics for item in sublist])

    def _is_anafora(self, sentence):
        ls = sentence.lower().split()
        return ls[0] in ANAFORA_BLACKLIST
