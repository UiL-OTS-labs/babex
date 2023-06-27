"""This script collects translatable messages from .vue and .ts files
based on calls to the translation function _()
It creates two json files containing en and nl messages in the src folders
"""
import re
import json
from pathlib import Path
from itertools import chain
from functools import partial


def collect_messages(language, output_path):
    try:
        existing = json.load(open(output_path))
    except FileNotFoundError:
        existing = {}

    i18n_re = re.compile(r'_\([\'"](.+?)[\'"]\)')

    with open(output_path, 'w') as out:
        p = partial(print, file=out)
        p('{\n')
        for f in chain(Path('src').rglob('*.vue'), Path('src').rglob('*.ts')):
            for idx, line in enumerate(open(f)):
                results = i18n_re.findall(line)
                for result in results:
                    # this is a silly trick to get around the fact that JSON doesn't officially support comments
                    # also the reason why json.dump isn't being used
                    p(f'"//": "{f}:{idx}",')

                    m = existing.get(result)
                    if m is None:
                        p(f'"{result}": null,')
                    else:
                        p(f'"{result}"', '"{}",'.format(m), sep=': ')

        # empty 'comment' field to deal with trailing comma
        p('\n"//": ""')
        p('}')


def main():
    target = 'src/messages.{}.json'
    collect_messages('en', target.format('en'))
    collect_messages('nl', target.format('nl'))


if __name__ == '__main__':
    main()
