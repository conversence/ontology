from sys import argv
from os.path import abspath

from simplejson import load, dump
from rdflib import ConjunctiveGraph
from pyld import jsonld


def convert(src, dest, npm, format='trig'):
    quads = jsonld.to_rdf('file:'+src, {'format': 'application/nquads'})
    g = ConjunctiveGraph()
    g.parse(data=quads, format='nquads')
    with open(dest, 'w') as f:
        f.write(g.serialize(format=format))

if __name__ == '__main__':
    convert(*argv[1:])
