#!/usr/bin/python
from argparse import ArgumentParser
from os.path import join, dirname

from simplejson import load

def check_keys(json, context):
    suspicious = set()
    for key, value in json.iteritems():
        if key[0] == '@':
            assert key[1:] in ('graph', 'id', 'type', 'language', 'context', 'value'), 'unknown @:'+key
            if key == '@context':
                continue
            if key == '@type':
                if value not in context:
                    suspicious.add(value)
        elif ':' in key:
            suspicious.add(key)
        else:
            if key not in context:
                suspicious.add(key)
        if isinstance(value, dict):
            suspicious.update(check_keys(value, context))
        elif isinstance(value, list):
            for val in value:
                if isinstance(val, dict):
                    suspicious.update(check_keys(val, context))
    return suspicious

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('input_fname', help="the input file")
    args = parser.parse_args()
    json = load(open(args.input_fname))
    context = load(open(join(dirname(__file__), 'context.jsonld')))
    suspicious = list(check_keys(json, context['@context']))
    suspicious.sort()
    for key in suspicious:
        print key
