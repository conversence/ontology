#!/usr/bin/python
import sys
import re
from argparse import ArgumentParser, FileType

from simplejson import load, dump
from rdflib import ConjunctiveGraph, BNode
from pyld import jsonld


def convert(context, input, output, input_format):
    context = load(context)
    g = ConjunctiveGraph()
    g.parse(data=input.read(), format=input_format)
    # It should be as simple as
    # f.write(g.serialize(format='json-ld', indent=2, context=context))
    # Bug in rdflib: Above loses the TextPositionSelector.
    quads = g.serialize(format='nquads')
    # The anonymous graph alone has a blank ID:
    blank_graph_ids = [h.identifier for h in g.contexts()
                       if isinstance(h.identifier, BNode)]
    if len(blank_graph_ids):
        assert len(blank_graph_ids) == 1
        # Remove the blank ID from the quads we give to pyld
        quads = re.sub(' %s \.' % blank_graph_ids[0].n3(), '.', quads)
    json = jsonld.from_rdf(quads)
    jsonc = jsonld.compact(json, context)
    # context does not have to be included
    jsonc['@context'] = 'http://purl.org/catalyst/jsonld'
    dump(jsonc, output, indent="  ")

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('--context', '-c', type=FileType('r'),
        help="The context file")
    parser.add_argument('--format', '-f', default='trig',
        help="The input format (as defined in rdflib)")
    parser.add_argument('--output', '-o', type=FileType('w'),
        default=sys.stdout, help="the output file")
    parser.add_argument('input_fname', help="the input file", type=FileType('r'))
    args = parser.parse_args()
    context = args.context
    if not context:
        import requests
        context = requests.get('http://purl.org/catalyst/jsonld')
    convert(context, args.input_fname, args.output, args.format)
