from urllib.request import Request, urlopen
from bs4 import BeautifulSoup
from bs4.element import Comment
import re

class DifferenceBetween():

    def __init__(self, article, topics):
        self.article = article

        self.definitions = {}
        # topics = self._extractHeaderTopics(link)
        for topic in topics:
            self.definitions[topic] = None


    def extractDefinitions(self):
        self._extractDefFromTable()
        if self._all_definitions_found():
            return self.definitions

        self._search_for_h3_that_starts_with_definition_of()
        if self._all_definitions_found():
            return self.definitions

        self._extractDefFromParagraph()
        return self.definitions


    def _to_be_def_topics(self):
        return [topic for topic in self.definitions.keys() if self.definitions[topic] == None]

    def _all_definitions_found(self):
        return all(_def != None for _def in self.definitions.values())

    def _extractDefFromTable(self):
        topics = self._to_be_def_topics()
        tables = self.article.find_all('table')
        if len(tables) == 0:
            return []

        for table in tables:
            try:
                if len(topics) == 2:
                    self._extract_def_from_table_with_2_topics(table, topics)
                elif len(topics) == 3:
                    self._extract_def_from_table_with_3_topics(table, topics)
            except:
                continue
        return

    def _extract_def_from_table_with_3_topics(self, table, topics):
        table_title = table.find_all('h3')[0].get_text()
        table_trs = table.find_all('tr')
        table_tds = table_trs[1].find_all('td')

        def_td = table_tds[0].get_text().lower()
        if def_td == 'definition' or def_td == 'refundability':
            def_trs = [table_trs[2], table_trs[3], table_trs[4]]
            def_tds = [tr.find_all('td')[1] for tr in def_trs]
            defs = [self._get_first_sentence(td.get_text()) for td in def_tds]
            for i, topic in enumerate(topics):
                self.definitions[topic] = defs[i]


    def _extract_def_from_table_with_2_topics(self, table, topics):
        titles = table.find_all('h3')
        table_trs = table.find_all('tr')
        table_title = table_trs[0].get_text()

        searching_for_a = '-'.join(topics[0].split())
        searching_for_b = '-'.join(topics[1].split())
        for table_title in self._parse_table_title(table_title):

            if (searching_for_a in table_title and '-vs-' in table_title)\
              or\
              (searching_for_b in table_title and '-vs-' in table_title):

              table_trs = table.find_all('tr')

              def_tds = table_trs[1].find_all('td')
              _def1 = self._get_first_sentence(def_tds[0].get_text())
              _def2 = self._get_first_sentence(def_tds[1].get_text())

              if len(_def1.split()) > 3:
                  self.definitions[topics[0]] = _def1
              if len(_def2.split()) > 3:
                  self.definitions[topics[1]] = _def2


    def _parse_table_title(self, txt):
        table_title = txt.lower()
        title_with_space = re.sub(r'([^\s\w]|_)+', ' ', table_title)
        title_without_space = re.sub(r'([^\s\w]|_)+', '', table_title)

        return ['-'.join(title_with_space.split()), '-'.join(title_without_space.split())]

    def _get_first_sentence(self, txt):
        txt = ' '.join(txt.split()) #clean from \t or \n or spaces
        txt = txt.split('. ')
        return txt[0]


  #---------

    def _extractDefFromParagraph(self):
        topics = self._to_be_def_topics()
        if len(topics) == 0:
            return

        entrycontent = self.article.find("div", { "class" : "entry-content" })
        h2s = entrycontent.find_all('h2')
        ps = entrycontent.find_all('p')
        tags = h2s + ps

        for topic in topics:
            what_is = f'what is {topic}'
            what_is_a = f'what is a {topic}'
            what_is_an = f'what is an {topic}'
            what_are = f'what are {topic}'
            what_does = f'what does {topic}'
            who_is_a = f'who is a {topic}'
            who_is = f'who is {topic}'
            topic_meaning = f'{topic} meaning origin and features'

            for tag in tags:
                h2_text = tag.get_text().lower().strip();
                h2_text = ' '.join(h2_text.split())
                h2_text = re.sub(r'([^\s\w]|_)+', ' ', h2_text)

                if h2_text.startswith(what_is[0:-2] if len(topic) > 3 else what_is) \
                  or h2_text.startswith(what_is_a[0:-2] if len(topic) > 3 else what_is_a) \
                  or h2_text.startswith(what_is_an[0:-2] if len(topic) > 3 else what_is_an ) \
                  or h2_text.startswith(what_are[0:-2] if len(topic) > 3 else what_are) \
                  or h2_text.startswith(what_does[0:-2] if len(topic) > 3 else what_does)\
                  or h2_text.startswith(who_is_a[0:-2] if len(topic) > 3 else who_is_a)\
                  or h2_text.startswith(who_is[0:-2] if len(topic) > 3 else who_is)\
                  or h2_text.startswith(topic + ' –'):

                    definitionP = tag.findNext('p')
                    txt = definitionP.get_text().split('.')[0] + '.'
                    if 'there is no difference' in txt:
                        continue

                    if 'difference between' in txt:
                        continue
                    if 'has two different meanings' in txt or 'first let us start off with' in txt:
                        txt = definitionP.get_text().split('.')[1] + '.'

                    if topic[0:-2] in txt.lower() or topic.split()[0] in txt.lower():
                        self.definitions[topic] = ' '.join(txt.split())
                        break

                elif ' '.join(h2_text.split()) == topic_meaning:
                    definitionP = tag.findNext('p')
                    txt = definitionP.get_text().split('.')[0] + '.'

                    if topic[0:-2] in txt.lower() or topic.split()[0] in txt.lower():
                        self.definitions[topic] = ' '.join(txt.split())
                        break
        return


    def _search_for_h3_that_starts_with_definition_of(self):
        topics = self._to_be_def_topics()
        if len(topics) == 0:
            return
        h3s = self.article.findAll('h3')
        for h3 in h3s:
            h3txt = ' '.join(h3.get_text().lower().split())
            if h3txt.startswith('definition of noun'):
                first_def = h3.findNext('p')
                second_def = first_def.findNext('p')

                for topic in topics:
                    if first_def.get_text().startswith(topic[0:-2]):
                        self.definitions[topic] = first_def
                    if second_def.get_text().startswith(topic[0:-2]):
                        self.definitions[topic] = second_def

            elif h3txt.startswith('definition of') or h3txt.startswith('definitions of'):
                try:
                    first_def = h3.findNext('p')
                    second_def = first_def.findNext('p')
                    if ':' in first_def.get_text() and ':' in second_def.get_text():
                        _topic, _def = first_def.get_text().split(':')
                        self.definitions[_topic.lower()] = ' '.join(_def.split())

                        _topic, _def = second_def.get_text().split(':')
                        self.definitions[_topic.lower()] = ' '.join(_def.split())
                except:
                    continue
