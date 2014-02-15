#!/usr/bin/python
from itertools import chain
import argparse
from StringIO import StringIO

from pygraphviz import AGraph
from rdflib import Graph, RDF, OWL, RDFS, BNode, XSD, Namespace
# from FuXi.Horn.HornRules import HornFromN3
# from FuXi.Rete.Util import generateTokenSet
# from FuXi.Rete.RuleStore import SetupRuleStore

# rule_store, rule_graph, network = SetupRuleStore(makeNetwork=True)
# for rule in HornFromN3('rdfs-rules.n3'):
#     network.buildNetworkFromClause(rule)


def normalize_label(s):
    s = s.lower()
    s = ''.join(s.split())
    s = ''.join(s.split('_'))
    s = ''.join(s.split('-'))
    return s


def list_content(rdflist, graph):
    for o in graph.transitive_objects(rdflist, RDF.rest):
        if o != RDF.nil:
            yield graph.objects(o, RDF.first).next()


def convert(graph, desired_ns=[], exclude_ns=[]):
    # graph.parse('rdf-schema.ttl', format='turtle')
    # network.feedFactsToAdd(generateTokenSet(graph))
    # for n in network.inferredFacts.triples((None, None, None)):
    #     graph.add(n)

    agraph = AGraph(directed=True, clusterrank="global", rankdir="LR")
    namespaces = {}
    nsm = graph.namespace_manager
    deferred_resources = set()
    included_resources = set()

    def prefix(ressource):
        return nsm.qname(ressource).split(':')[0]

    def add_ressource(ressource):
        if ressource not in included_resources:
            qname = nsm.qname(ressource)
            prefix = qname.split(':')[0]
            shape = 'rect' if (
                ressource, RDF.type, OWL.Class) in graph else 'oval'
            color = 'black' if prefix in desired_ns else 'grey'
            if prefix in namespaces:
                namespaces[prefix].add_node(qname, shape=shape, color=color)
            else:
                agraph.add_node(qname, shape=shape, color=color)
            included_resources.add(ressource)
            if ressource in deferred_resources:
                deferred_resources.remove(ressource)

    def add_edge(r1, r2, **kwargs):
        pr1, pr2 = prefix(r1), prefix(r2)
        if pr1 in exclude_ns or pr2 in exclude_ns:
            return
        if pr1 in desired_ns or pr2 in desired_ns:
            add_ressource(r1)
            add_ressource(r2)
            agraph.add_edge(nsm.qname(r1), nsm.qname(r2), **kwargs)

    for kprefix, namespace in graph.namespaces():
        namespaces[kprefix] = agraph.add_subgraph(
            name="cluster_"+kprefix, color="grey")
    for k in graph.subjects(RDF.type, OWL.Class):
        if isinstance(k, BNode):
            continue
        qname = nsm.qname(k)
        kprefix = prefix(k)
        if kprefix in exclude_ns:
            continue
        elif kprefix in desired_ns:
            add_ressource(k)
        else:
            deferred_resources.add(k)
    for (s, p, o) in chain(graph.triples((None, RDFS.subClassOf, None)),
            graph.triples((None, OWL.subClassOf, None))):
        if isinstance(s, BNode) or isinstance(o, BNode):
            continue
        add_edge(s, o, arrowhead='empty', color="blue")
    prop_types = [OWL.Property, OWL.AnnotationProperty, OWL.DatatypeProperty,
                  OWL.AsymmetricProperty, OWL.ObjectProperty,
                  OWL.FunctionalProperty, OWL.InverseFunctionalProperty]
    properties = set()
    for prop in prop_types:
        properties.update(graph.subjects(RDF.type, prop))
    for k in properties:
        if isinstance(k, BNode):
            continue
        qname = nsm.qname(k)
        kprefix = prefix(k)
        if kprefix in exclude_ns:
            continue
        elif kprefix in desired_ns:
            add_ressource(k)
        else:
            deferred_resources.add(k)
    for (s, p, o) in chain(graph.triples((None, RDFS.subPropertyOf, None)),
            graph.triples((None, OWL.subPropertyOf, None))):
        if isinstance(s, BNode) or isinstance(o, BNode):
            continue
        add_edge(s, o, arrowhead='empty', color="blue")

    for (s, p, o) in graph.triples((None, OWL.equivalentClass, None)):
        if isinstance(s, BNode) or isinstance(o, BNode):
            continue
        add_edge(s, o, arrowhead="odot", arrowtail="odot", color="blue")
    for (s, p, o) in graph.triples((None, RDFS.domain, None)):
        if isinstance(s, BNode):
            continue
        if isinstance(o, BNode):
            for o2 in graph.objects(o, OWL.unionOf):
                for o3 in list_content(o2, graph):
                    add_edge(o3, s, arrowhead="open")
            for o2 in graph.objects(o, OWL.intersectionOf):
                for o3 in list_content(o2, graph):
                    add_edge(o3, s, arrowhead="open")
            continue
        add_edge(o, s, arrowhead="open")
    for (s, p, o) in graph.triples((None, RDFS.range, None)):
        if isinstance(s, BNode):
            continue
        if isinstance(o, BNode):
            for o2 in graph.objects(o, OWL.unionOf):
                for o3 in list_content(o2, graph):
                    add_edge(s, o3, arrowhead="open")
            for o2 in graph.objects(o, OWL.intersectionOf):
                for o3 in list_content(o2, graph):
                    add_edge(s, o3, arrowhead="open")
            continue
        add_edge(s, o, arrowhead="open")
    for (s, p, o) in graph.triples((None, OWL.inverseOf, None)):
        if isinstance(s, BNode) or isinstance(o, BNode):
            continue
        if str(o) < str(s):
            s, o = o, s
        add_edge(o, s, arrowhead="crow", arrowtail="crow", dir="both")

    for ressource in included_resources:
        labels = graph.objects(ressource, RDFS.label)
        en_labels = [l for l in labels if l.language == 'eng']
        if en_labels:
            label = en_labels[0]
            qname = nsm.qname(ressource)
            prefix, name = qname.split(':', 1)
            if normalize_label(name) != normalize_label(label):
                node = agraph.get_node(qname)
                node.attr['label'] = "%s\n(%s)" % (qname, label)

    return agraph


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Process some ontologies.')
    parser.add_argument('--format', default='turtle')
    parser.add_argument('--desired_ns', nargs='+', default=[])
    parser.add_argument('--exclude_ns', nargs='+',
                        default=['xsd', 'owl', 'rdfs', 'rdf'])
    parser.add_argument('--output', default=None)
    parser.add_argument('--files', nargs='+')
    args = parser.parse_args()
    graph = Graph()
    for gfile in args.files:
        graph.parse(open(gfile), format=args.format)
    agraph = convert(graph, args.desired_ns, args.exclude_ns)
    if args.output:
        agraph.write(args.output)
    else:
        print agraph.string().encode('utf-8')
