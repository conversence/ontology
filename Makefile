# Prerequisites:
# http://www.graphviz.org/
# Raptor from http://librdf.org/
# https://github.com/RDFLib/rdflib (pip install rdflib)
# https://github.com/digitalbazaar/pyld (pip install pyld)
#
# Ubuntu:  
# sudo apt-get install python-pygraphviz raptor2-utils python-simplejson
# sudo pip install 'rdflib>=4' pyld


dotfiles = ibis.dot version.dot aif.dot vote.dot sioc.dot idea.dot assembl.dot ibis_idea.dot ibis_aif.dot ibis_pa.dot catalyst_core.dot reln_aif.dot reln_pa_ibis.dot
sourcefiles = version.ttl assembl_core.ttl catalyst_idea.ttl AIF-RDF.core.ttl pa_ibis.ttl sioc.ttl foaf.ttl catalyst_ibis.ttl catalyst_vote.ttl catalyst_core.ttl
pdf_files  := $(subst .dot,.pdf,$(dotfiles))

all: $(dotfiles) example.json

clean:
	rm -f $(dotfiles) $(pdf_files) example.json foaf.ttl pa_ibis.ttl sioc.ttl sioc.rdf.xml foaf.ttl pa_ibis.ttl foaf.rdf.xml


ibis.dot: catalyst_ibis.ttl $(sourcefiles)
	python rdf2dot.py --output $@ --exclude_ns xsd rdf rdfs owl pa_ibis aif --desired_ns ibis --files $(sourcefiles)

ibis_aif.dot: catalyst_ibis.ttl $(sourcefiles)
	python rdf2dot.py --output $@ --exclude_ns xsd rdf rdfs owl pa_ibis --desired_ns ibis --files $(sourcefiles)

ibis_pa.dot: catalyst_ibis.ttl $(sourcefiles)
	python rdf2dot.py --output $@ --exclude_ns xsd rdf rdfs owl aif --desired_ns ibis --files $(sourcefiles)

idea.dot: catalyst_idea.ttl $(sourcefiles)
	python rdf2dot.py --output $@ --exclude_ns xsd rdf rdfs owl ibis --desired_ns idea --files $(sourcefiles)

vote.dot: catalyst_vote.ttl $(sourcefiles)
	python rdf2dot.py --output $@ --exclude_ns xsd rdf rdfs owl --desired_ns vote --files $(sourcefiles)

assembl.dot: assembl_core.ttl $(sourcefiles)
	python rdf2dot.py --output $@ --exclude_ns xsd rdf rdfs owl --desired_ns assembl --files $(sourcefiles)

catalyst_core.dot: catalyst_core.ttl $(sourcefiles)
	python rdf2dot.py --output $@ --exclude_ns xsd rdf rdfs owl --desired_ns catalyst --files $(sourcefiles)

reln_pa_ibis.dot: catalyst_paibis.ttl $(sourcefiles)
	python rdf2dot.py --output $@ --exclude_ns xsd rdf rdfs owl --desired_ns pa_ibis ibis --files catalyst_paibis.ttl $(sourcefiles)

reln_aif.dot: catalyst_aif.ttl $(sourcefiles)
	python rdf2dot.py --output $@ --exclude_ns xsd rdf rdfs owl --desired_ns idea ibis --files catalyst_aif.ttl $(sourcefiles)

version.dot: version.ttl $(sourcefiles)
	python rdf2dot.py --output $@ --exclude_ns xsd rdfs owl --desired_ns version --files $(sourcefiles)

aif.dot: AIF-RDF.core.ttl $(sourcefiles)
	python rdf2dot.py --output $@ --exclude_ns xsd rdf rdfs owl --desired_ns aif --files AIF-RDF.core.ttl

sioc.dot: sioc.ttl $(sourcefiles)
	python rdf2dot.py --output $@ --exclude_ns xsd rdf rdfs owl --desired_ns sioc --files $(sourcefiles)

ibis_idea.dot: catalyst_idea.ttl $(sourcefiles)
	python rdf2dot.py --output $@ --exclude_ns xsd rdf rdfs owl vote assembl pa_ibis --desired_ns idea ibis --files $(sourcefiles)

pdf: $(pdf_files)

%.pdf : %.dot
	dot -Tpdf -o $@ $<

%.json: %.trig context.jsonld
	python save_jsonld.py -c context.jsonld -o $@ $<

pa_ibis.ttl:
	curl -o $@ http://privatealpha.com/ontology/ibis/1

sioc.rdf.xml:
	curl -o $@ http://rdfs.org/sioc/ns

foaf.rdf.xml:
	curl -H 'Accept: application/rdf+xml' -o $@ http://xmlns.com/foaf/0.1/

%.ttl: %.rdf.xml
	rapper -i rdfxml -o turtle $< > $@

