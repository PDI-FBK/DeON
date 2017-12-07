from bs4 import BeautifulSoup
import re


class Dictionary():

    def __init__(self, file_path):
        self.container = BeautifulSoup(open(file_path), "html.parser")\
                          .find('div', {'class': 'center-well-container'})

    def extract_definition(self):
        boxes = self.container.find_all('div', {'class': 'source-box'})
        definitions = []
        for box in boxes:
            topic = self._get_topic(box)
            if topic:
                definitions.append(self._extract_from_def_list(box, topic))
        return definitions

    def _extract_from_def_list(self, box, topic):
        definitions = {}
        def_contents = box.find_all('div', {'class': 'def-pbk'})
        if len(def_contents) == 0:
            def_contents = box.find_all('section', {'class': 'def-pbk'})

        for def_content in def_contents:
            contents = self._get_definition(def_content, topic)
            if contents is []:
                continue
            for content in contents:
                definitions[topic] = (definitions.get(topic, []))
                definitions[topic].append(content)

        return definitions

    def _get_definition(self, def_content, topic):
        res = []
        if len(def_content.find_all('a')) > 0:
            return res

        header = def_content.find('header')
        if header is None:
            header = def_content

        if not self._is_noun(header.get_text()):
            return res

        defcontents = def_content.findAll('div', {'class': 'def-content'})
        for content in defcontents:
            # if content has <ol> do not consider it
            if len(content.find_all('ol')) > 0:
                continue
            content = ' '.join(content.get_text().split())
            content = content.split('. ')[0]
            content += '.' if not content[-1] == '.' else ''
            if len(content.split()) == 1:
                continue
            if content.startswith('('):
                domain, other = self._extract_domain(content)
                content = 'In {}, {} is {}'.format(domain, topic, other)
            else:
                content = topic + ' is ' + content
            if re.search(r"\d+(.\d+)?\s[ba].?c[\s,]", content):
                continue
            res.append(content)
        return res

    def _is_noun(self, txt):
        for word in txt.split():
            if word.startswith('noun'):
                return True
            return False

    def _extract_domain(self, txt):
        first = '('
        last = ')'
        start = txt.index(first) + len(first)
        end = txt.index(last, start)
        domain = txt[start:end]
        ls = domain.split()
        if ls[0].lower() == 'in':
            domain = ' '.join(ls[1:])
        return domain, txt[end + 1:]

    def _get_topic(self, box):
        header_topic = box.find('div', {'class': 'header-row'})
        if header_topic:
            header_topic = header_topic.get_text().split()
            header_topic = ' '.join(header_topic)
            header_topic = header_topic.split(' or ')[0]
            header_topic = header_topic.split(',')[0]
            header_topic = header_topic.strip()
            header_topic = re.sub("\d+", "", header_topic)
            return header_topic
        return None
