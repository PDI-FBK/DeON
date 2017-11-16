import sys


def print_progress(msg, done, total='oo'):
    sys.stdout.write('\r')
    sys.stdout.write('\t{} {}/{}'.format(msg, done, total))
    sys.stdout.flush()

 def save_output(file, definition, _def, url, topic='?', topic_pos='?'):
        with open(file, 'a') as f:
            f.write('{}\t{}\t{}\t{}\t{}\n'.format(definition, topic, topic_pos, _def, url))
