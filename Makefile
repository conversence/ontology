# Prerequisites:
# http://www.graphviz.org/
# Raptor from http://librdf.org/
# https://github.com/RDFLib/rdflib (pip install rdflib)
# https://github.com/digitalbazaar/pyld (pip install pyld)

dotfiles = ibis.dot version.dot aif.dot vote.dot sioc.dot idea.dot assembl.dot ibis_idea.dot
sourcefiles = version.ttl assembl_core.ttl catalyst_idea.ttl AIF-RDF.core.ttl pa_ibis.ttl sioc.ttl foaf.ttl catalyst_ibis.ttl catalyst_vote.ttl
pdf_files  := $(subst .dot,.pdf,$(dotfiles))

all: $(dotfiles) example.json

clean:
	rm -f $(dotfiles) $(pdf_files) example.json


ibis.dot: catalyst_ibis.ttl
	python rdf2dot.py --output $@ --exclude_ns xsd rdf rdfs owl --desired_ns ibis --files $(sourcefiles)

idea.dot: catalyst_idea.ttl
	python rdf2dot.py --output $@ --exclude_ns xsd rdf rdfs owl --desired_ns idea --files $(sourcefiles)

vote.dot: catalyst_vote.ttl
	python rdf2dot.py --output $@ --exclude_ns xsd rdf rdfs owl --desired_ns vote --files $(sourcefiles)

assembl.dot: assembl_core.ttl
	python rdf2dot.py --output $@ --exclude_ns xsd rdf rdfs owl --desired_ns assembl --files $(sourcefiles)

version.dot: version.ttl
	python rdf2dot.py --output $@ --exclude_ns xsd rdfs owl --desired_ns version --files $(sourcefiles)

aif.dot: AIF-RDF.core.ttl
	python rdf2dot.py --output $@ --exclude_ns xsd rdf rdfs owl --desired_ns aif --files AIF-RDF.core.ttl

sioc.dot: sioc.ttl
	python rdf2dot.py --output $@ --exclude_ns xsd rdf rdfs owl --desired_ns sioc --files $(sourcefiles)

ibis_idea.dot: catalyst_idea.ttl
	python rdf2dot.py --output $@ --exclude_ns xsd rdf rdfs owl vote assembl pa_ibis --desired_ns idea ibis --files $(sourcefiles)

pdf: $(pdf_files)

%.pdf : %.dot
	dot -Tpdf -o $@ $<

%.json: %.trig context.jsonld
	python save_jsonld.py context.jsonld $< $@

pa_ibis.ttl:
	curl -o $@ http://privatealpha.com/ontology/ibis/1

sioc.rdf.xml:
	curl -o $@ http://rdfs.org/sioc/ns

foaf.rdf.xml:
	curl -o $@ http://xmlns.com/foaf/0.1/

%.ttl: %.rdf.xml
	rapper -i rdfxml -o turtle $< > $@

