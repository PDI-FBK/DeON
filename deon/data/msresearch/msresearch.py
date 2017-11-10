from deon.data.datasource import DataSource
import os
import urllib.request


class MsResearchSource(DataSource):
    KEY = 'msresearch'
    _LINK = 'http://taln.upf.edu/web_old/system/files/resources_files/ms_research_defs-nodefs.txt'
    _OUT_FILE = 'msresearch.tsv'

    def pull(self, dest):
        f_path = os.path.join(dest, 'msresearch.txt')
        with open(f_path, 'wb') as f_out:
            f_out.write(urllib.request.urlopen(self._LINK).read())

        source = open(f_path)
        f_out_path = os.path.join(dest, self._OUT_FILE)
        with open(f_out_path, 'w') as f_out:
            for line in source:
                line = line.strip()
                if not line:
                    continue

                is_def, phrase = line.split('/', 1)
                def_flag = is_def == 'DEF'
                _def = 1 if def_flag else 0
                topic = ''
                pos = ''
                if _def:
                    topic, pos = self._extract_topic_pos(phrase)
                out_line = "{}\t{}\t{}\t{}\t{}\n"\
                            .format(phrase, topic, pos, _def, self.KEY)
                f_out.write(out_line)
        return f_out_path

    def _extract_topic_pos(self, phrase):
        topic = phrase.split(' is ')[0].lower()
        start_pos = 0
        topic = topic[0: topic.find('(') if topic.find('(') > -1 else len(topic)]
        if topic.startswith('a '):
            topic = topic[2:]
            start_pos = 1
        elif topic.startswith('an '):
            topic = topic[3:]
            start_pos = 1
        elif topic.startswith('the '):
            topic = topic[4:]
            start_pos = 1
        else:
            return topic, ','.join([str(x) for x in \
                range(start_pos, len(topic.split(' ')))])

        return topic, ','.join([str(x) for x in \
                range(start_pos, len(topic.split(' ')) + 1)])
