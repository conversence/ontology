#!/usr/bin/python
import sys
from argparse import ArgumentParser, FileType

import simplejson as json
from rdflib import ConjunctiveGraph

context_url = 'http://purl.org/conversence/jsonld'


def convert(context, input, output, input_format):
    context = json.load(context)
    g = ConjunctiveGraph()
    g.parse(data=input.read(), format=input_format)
    # It should be as simple as
    # f.write(g.serialize(format='json-ld', indent=2, context=context))
    # Bug in rdflib: Above loses the TextPositionSelector.
    jgraph = json.loads(g.serialize(format='json-ld', context=context))
    jgraph['@context'] = context_url
    json.dump(jgraph, output, indent="  ")

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('--context', '-c', type=FileType('r'),
        help="The context file")
    parser.add_argument('--format', '-f', default='trig',
        help="The input format (as defined in rdflib)")
    parser.add_argument('--output', '-o', type=FileType('w'),
        default=sys.stdout, help="the output file")
    parser.add_argument('input_fname', help="the input file",
        type=FileType('r'))
    args = parser.parse_args()
    context = args.context
    if not context:
        import requests
        context = requests.get(context_url)
    convert(context, args.input_fname, args.output, args.format)
