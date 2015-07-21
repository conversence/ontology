import sys
import os
from os.path import exists, join
from itertools import chain
from collections import defaultdict

import simplejson as json
import rdflib
from rdflib.namespace import RDFS, DCTERMS


def extract_labels(graph, prop):
    labelsBySubject = defaultdict(dict)
    for s,p,o in c.triples((None, prop, None)):
        labelsBySubject[s][o.language] = o
    return labelsBySubject

LANGS = ['fr']

if __name__ == '__main__':
    c = rdflib.ConjunctiveGraph()
    for f in sys.argv[1:]:
        c.parse(open(f), format='turtle')

    labelsBySubject = extract_labels(c, RDFS.label)
    descriptionsBySubject = extract_labels(c, DCTERMS.description)
    for lang in LANGS:
        if not exists(lang):
            os.mkdir(lang)
        dirname = join(lang, 'LC_MESSAGES')
        if not exists(dirname):
            os.mkdir(dirname)
        with open(join(dirname, 'ontology.po'), 'w') as f:
            for labels in chain(
                    labelsBySubject.itervalues(),
                    descriptionsBySubject.itervalues()):
                if 'en' in labels and lang in labels:
                    f.write((u'msgid "%s"\nmsgstr"%s"\n\n' % (
                        labels['en'], labels[lang])).encode('utf-8'))
    c2 = rdflib.Graph()
    subjects = set(chain(labelsBySubject.iterkeys(),
                         descriptionsBySubject.iterkeys()))
    for s in subjects:
        label = labelsBySubject[s].get('en', None)
        if label is not None:
            c2.add((s, RDFS.label, label))
        desc = descriptionsBySubject[s].get('en', None)
        if desc is not None:
            c2.add((s, DCTERMS.description, desc))
    with open('labels.jsonld', 'w') as f:
        f.write(c2.serialize(format="json-ld", context={
            "@language": "en",
            "label": str(RDFS.label),
            "description": str(DCTERMS.description)
        }))
