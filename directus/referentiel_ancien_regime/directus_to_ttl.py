import json
from rdflib import Graph, Literal, Namespace, DCTERMS, RDF, RDFS, SKOS, URIRef, URIRef as u, Literal as l
import argparse
from pprint import pprint
from sherlockcachemanagement import Cache

# Arguments
parser = argparse.ArgumentParser()
parser.add_argument("--json")
parser.add_argument("--ttl")
parser.add_argument("--cache")
args = parser.parse_args()

# Cache
cache = Cache(args.cache)

############################################################################################
## INITIALISATION DU GRAPHE ET NAMESPACES
############################################################################################

output_graph = Graph()

crm_ns = Namespace("http://www.cidoc-crm.org/cidoc-crm/")
crmdig_ns = Namespace("http://www.ics.forth.gr/isl/CRMdig/")
iremus_ns = Namespace("http://data-iremus.huma-num.fr/id/")
lrmoo_ns = Namespace("http://www.cidoc-crm.org/lrmoo/")
sdt_ns = Namespace("http://data-iremus.huma-num.fr/datatypes/")
sherlock_ns = Namespace("http://data-iremus.huma-num.fr/ns/sherlock#")

output_graph.bind("crm", crm_ns)
output_graph.bind("crmdig", crmdig_ns)
output_graph.bind("dcterms", DCTERMS)
output_graph.bind("skos", SKOS)
output_graph.bind("lrmoo", lrmoo_ns)
output_graph.bind("sdt", sdt_ns)
output_graph.bind("she_ns", sherlock_ns)

a = RDF.type


def crm(x):
	return URIRef(crm_ns[x])


def dig(x):
	return URIRef(crmdig_ns[x])


def lrm(x):
	return URIRef(lrmoo_ns[x])


def she(x):
	return URIRef(iremus_ns[x])


def she_ns(x):
	return URIRef(sherlock_ns[x])


def t(s, p, o):
	output_graph.add((s, p, o))


############################################################################################
## RECUPERATION DES DONNEES
############################################################################################

E32_personnes_uri = u(iremus_ns["947a38f0-34ac-4c54-aeb7-69c5f29e77c0"])
t(E32_personnes_uri, a, crm("E32_Authority_Document"))
t(E32_personnes_uri, crm("P1_is_identified_by"), l("Noms de personnes"))

with open(args.json) as f:
	json_file = json.load(f)

	for personne in json_file["data"]["personnes"]:
		E21_uuid = personne["id"]
		E21_uri = she(E21_uuid)
		t(E21_uri, a, crm("E21_Person"))
		t(E32_personnes_uri, crm("P71_lists"), E21_uri)

		# Appellation
		E41_uri = she(cache.get_uuid(["personnes", E21_uri, "E41"], True))
		t(E21_uri, crm("P1_is_identified_by"), E41_uri)
		t(E41_uri, a, crm("E41_Appellation"))
		t(E41_uri, RDFS.label, l(personne["label"]))
		t(E41_uri, crm("P2_has_type"), SKOS.prefLabel)


############################################################################################
## SERIALISATION DU GRAPHE
############################################################################################

serialization = output_graph.serialize(format="turtle", base="http://data-iremus.huma-num.fr/id/")
with open(args.ttl, "wb") as f:
	f.write(serialization)

cache.bye()