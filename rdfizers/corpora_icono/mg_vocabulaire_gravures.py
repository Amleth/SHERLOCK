import argparse
from sherlockcachemanagement import Cache
from rdflib import Graph, Namespace, DCTERMS, RDF, RDFS, SKOS, URIRef, XSD, URIRef as u, Literal as l

parser = argparse.ArgumentParser()
parser.add_argument("--xls")
parser.add_argument("--ttl")
parser.add_argument("--cache")
args = parser.parse_args()

cache = Cache(args.cache)

g = Graph()
iremus = Namespace("http://data-iremus.huma-num.fr/id/")
crm = Namespace("http://www.cidoc-crm.org/cidoc-crm/")
g.bind("crm", crm)
lrmoo = Namespace("http://www.cidoc-crm.org/lrmoo/")
g.bind("lrmoo", lrmoo)

F34_uuid = iremus['957985bf-e95a-4e29-b5ad-3520e2eea34e']
g.add((F34_uuid, RDF.type, lrmoo['F34_Controlled_Vocabulary']))
g.add((F34_uuid, crm['P1_is_identified_by'], l("Vocabulaire d'indexation des gravures du Mercure Galant")))
g.add((F34_uuid, DCTERMS.creator, iremus['ea287800-4345-4649-af12-7253aa185f3f']))




serialization = g.serialize(format="turtle", base="http://data-iremus.huma-num.fr/id/")
with open(args.ttl, "wb") as f:
    f.write(serialization)

cache.bye()
