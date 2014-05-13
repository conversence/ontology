#!/usr/bin/python
from sys import argv
from os.path import abspath
import re

from simplejson import load, dump
from rdflib import ConjunctiveGraph, BNode
from pyld import jsonld


def convert(context, src, dest):
    #context = abspath(context)
    with open(context) as f:
        context = load(f)
    g = ConjunctiveGraph()
    with open(src) as f:
        g.parse(data=f.read(), format='trig')
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
    with open(dest, 'w') as f:
        dump(jsonc, f, indent="  ")

if __name__ == '__main__':
    convert(*argv[1:])
