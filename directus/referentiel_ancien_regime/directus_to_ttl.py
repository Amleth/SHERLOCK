import json
from rdflib import Graph, Literal, Namespace, DCTERMS, RDF, RDFS, SKOS, URIRef, URIRef as u, Literal as l
import argparse
from pprint import pprint

# Arguments
parser = argparse.ArgumentParser()
parser.add_argument("--json")
parser.add_argument("--ttl")
args = parser.parse_args()

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

with open(args.json) as f:
	json_file = json.load(f)

	print(len(json_file["data"]["personnes"]))


############################################################################################
## SERIALISATION DU GRAPHE
############################################################################################

# serialization = output_graph.serialize(format="turtle", base="http://data-iremus.huma-num.fr/id/")
# with open(args.ttl, "wb") as f:
# 	f.write(serialization)
