from sys import argv
from os.path import abspath

from simplejson import load, dump
from rdflib import ConjunctiveGraph
from pyld import jsonld


def convert(context, src, dest):
    #context = abspath(context)
    with open(context) as f:
        context = load(f)
    g = ConjunctiveGraph()
    with open(src) as f:
        g.parse(data=f.read(), format='trig')

    with open(dest, 'w') as f:
        # f.write(g.serialize(format='json-ld', indent=4, context=context))
        # Bug in rdflib: Above loses the TextPositionSelector.
        quads = g.serialize(format='nquads')
        json = jsonld.from_rdf(quads)
        jsonc = jsonld.compact(json, context)
        dump(jsonc, f, indent="    ")

if __name__ == '__main__':
    convert(*argv[1:])
