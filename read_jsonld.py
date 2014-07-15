#!/usr/bin/python
import sys
from os.path import abspath
from argparse import ArgumentParser, FileType

from simplejson import load, dump
from rdflib import Graph, ConjunctiveGraph
from rdflib.namespace import NamespaceManager
from pyld import jsonld

npm = NamespaceManager(Graph())
npm.bind("owl", "http://www.w3.org/2002/07/owl#")
npm.bind("rdf", "http://www.w3.org/1999/02/22-rdf-syntax-ns#")
npm.bind("rdfs", "http://www.w3.org/2000/01/rdf-schema#")
npm.bind("xsd", "http://www.w3.org/2001/XMLSchema#")
npm.bind("trig", "http://www.w3.org/2004/03/trix/rdfg-1/")
npm.bind("foaf", "http://xmlns.com/foaf/0.1/")
npm.bind("dcterms", "http://purl.org/dc/terms/")
npm.bind("sioc", "http://rdfs.org/sioc/ns#")
npm.bind("oa", "http://www.openannotation.org/ns/")
npm.bind("idea", "http://purl.org/catalyst/idea#")
npm.bind("ibis", "http://purl.org/catalyst/ibis#")
npm.bind("assembl", "http://purl.org/assembl/core#")
npm.bind("catalyst", "http://purl.org/catalyst/core#")
npm.bind("version", "http://purl.org/catalyst/version#")
npm.bind("vote", "http://purl.org/catalyst/vote#")
npm.bind("eg_site", "http://www.assembl.net/")
npm.bind("eg_d1", "http://www.assembl.net/discussion/1/")
npm.bind("kmieg", "http://maptesting.kmi.open.ac.uk/api/")
npm.bind("kmiegnodes", "http://maptesting.kmi.open.ac.uk/api/nodes/")

def convert(input_fname, output, format='trig'):
    quads = jsonld.to_rdf('file:'+input_fname, {'format': 'application/nquads'})
    if format == 'nquads':
        output.write(quads.encode('utf-8'))
    else:
        g = ConjunctiveGraph()
        g.namespace_manager=npm
        g.parse(data=quads, format='nquads')
        for c in g.contexts():
            c.namespace_manager=npm
        output.write(g.serialize(format=format))

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('--format', '-f', default='trig',
        help="The output format (as defined in rdflib)")
    parser.add_argument('--output', '-o', type=FileType('w'), default=sys.stdout,
        help="the output file")
    parser.add_argument('input_fname', help="the input file")
    args = parser.parse_args()
    convert(**vars(args))
    args.output.close()
