#!/usr/bin/python
from argparse import ArgumentParser
from os.path import join, dirname

from rdflib import Graph, ConjunctiveGraph, RDF, OWL, RDFS, BNode, XSD, Namespace
from rdflib.namespace import (
    Namespace, NamespaceManager,
    RDF, RDFS, OWL, XSD, DC, DCTERMS, FOAF, SKOS)
from simplejson import load, dump

SIOC = Namespace('http://rdfs.org/sioc/ns#')
OA = Namespace('http://www.openannotation.org/ns/')
CATALYST = Namespace('http://purl.org/catalyst/core#')
IDEA = Namespace('http://purl.org/catalyst/idea#')
IBIS = Namespace('http://purl.org/catalyst/ibis#')
VOTE = Namespace('http://purl.org/catalyst/vote#')
VERSION = Namespace('http://purl.org/catalyst/version#')
ASSEMBL = Namespace('http://purl.org/assembl/core#')


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

ontology_files = [
    'rdf-schema.ttl',
    'owl.ttl',
    'assembl_core.ttl',
    'catalyst_aif.ttl',
    'catalyst_core.ttl',
    'catalyst_ibis.ttl',
    'catalyst_idea.ttl',
    'catalyst_vote.ttl',
    'dcterms.ttl',
    'foaf.ttl',
    'openannotation.ttl',
    'sioc.ttl',
    'version.ttl']

def load_ontology():
    from FuXi.Horn.HornRules import HornFromN3
    from FuXi.Rete.Util import generateTokenSet
    from FuXi.Rete.RuleStore import SetupRuleStore
    rule_store, rule_graph, network = SetupRuleStore(makeNetwork=True)
    for rule in HornFromN3('rdfs-rules.n3'):
        network.buildNetworkFromClause(rule)
    # for rule in HornFromN3('owl-rules.n3'):
    #     network.buildNetworkFromClause(rule)
    g = Graph(identifier='http://catalyst-fp8.eu/ontology')
    npm = NamespaceManager(g)
    g.namespace_manager = npm
    for name in ('SIOC','OA','CATALYST','IDEA','IBIS','VOTE','VERSION','ASSEMBL','OWL','RDF', 'OWL', 'RDFS', 'XSD'):
        npm.bind(name.lower(), globals()[name])
    for f in ontology_files:
        g.parse(join(dirname(__file__), f), format='turtle')
    network.feedFactsToAdd(generateTokenSet(g))
    for n in network.inferredFacts.triples((None, None, None)):
        g.add(n)
    return g

def in_range(g, resource, classes):
    for cls in classes:
        for r_class in g.objects(resource, RDF.type):
            if r_class == cls or (r_class, RDFS.subClassOf, cls) in g:
                return True

def check_props(g, ontology):
    props = {}
    for (s, p, o) in g.triples((None, None, None)):
        if p not in props:
            domain = list(g.objects(p, RDFS.domain))
            range_ =  list(g.objects(p, RDFS.range))
            props[p] = (domain, range_)
        domain, range_ = props[p]
        if domain and not in_range(s, domain):
            print "Not in domain: ", s, p, o
        if range_ and not in_range(o, range_):
            print "Not in range: ", s, p, o


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('--check_properties', '-p', action='store_true',
        help="check property domain and range against the ontology. Slow.")
    parser.add_argument('input_fname', help="the input file")
    args = parser.parse_args()
    json = load(open(args.input_fname))
    context = load(open(join(dirname(__file__), 'context.jsonld')))
    suspicious = list(check_keys(json, context['@context']))
    suspicious.sort()
    if suspicious:
        print "Suspicious keys:"
        for key in suspicious:
            print key
    if args.check_properties:
        from pyld import jsonld
        quads = jsonld.to_rdf('file:'+args.input_fname, {'format': 'application/nquads'})
        ontology = load_ontology()
        g = ConjunctiveGraph()
        g.namespace_manager = ontology.namespace_manager
        g.parse(data=quads, format='nquads')
        for c in g.contexts():
            c.namespace_manager = ontology.namespace_manager
        check_props(g, ontology)
