import sys
from subprocess import Popen, PIPE, DEVNULL


def print_progress(msg, done, total='oo', extra_msg=''):
    sys.stdout.write('\r')
    sys.stdout.write('\t{} {}/{} {}'.format(msg, done, total, extra_msg))
    sys.stdout.flush()


def save_output(file, definition, _def, url, topic='?', topic_pos='?'):
    with open(file, 'a') as f:
        f.write('{}\t{}\t{}\t{}\t{}\n'.format(definition, topic, topic_pos, _def, url))


def start_wcl_process():
    process = Popen(['java', '-jar', './target/wcl-wrapper.jar', '-l', 'en', '-t', './data/training/wiki_good.EN.html'], stdin=PIPE, stdout=PIPE, stderr=DEVNULL, cwd='/home/linnal/unitn/thesis/MSc/wcl-wrapper')
    return process


def query_wcl_for(process, topic, sentence):
    tmp = '{}\t{}\n'.format(topic, sentence)
    process.stdin.write(str.encode(tmp))
    process.stdin.flush()
    res = process.stdout.readline()
    res = res.decode("utf-8")
    res = res.split('\t')[-1].strip()
    return res == 'true'


def topic_position(topic, sentence):
    topics = topic.split()
    if len(topics) == 0:
        return None
    words = sentence.split()
    indexes = []
    for i, word in enumerate(words):
        if word == topics[0]:
            indexes.append(i)
    index = -1
    for index in indexes:
        i = index
        for topic in topics:
            if words[i] != topic:
                break
        break
    if index < 0:
        return None
    return ','.join([str(x) for x in range(index, (index + len(topics)))])