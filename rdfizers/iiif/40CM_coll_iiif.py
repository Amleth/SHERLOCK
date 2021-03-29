import xlrd
import argparse
from rdflib import Graph, Literal, Namespace, DCTERMS, RDF, RDFS, SKOS, URIRef, URIRef as u, Literal as l
import yaml
from sherlockcachemanagement import Cache

# Arguments
parser = argparse.ArgumentParser()
parser.add_argument("--iiif_excel")
parser.add_argument("--output_ttl")
parser.add_argument("--cache_40CM")
args = parser.parse_args()


# Cache
cache_40CM = Cache(args.cache_40CM)


# Initialisation du graphe
output_graph = Graph()


# Namespaces
crm_ns = Namespace("http://www.cidoc-crm.org/cidoc-crm/")
iremus_ns = Namespace("http://data-iremus.huma-num.fr/id/")
lrmoo_ns = Namespace("http://www.cidoc-crm.org/lrmoo/")
sdt_ns = Namespace("http://data-iremus.huma-num.fr/datatypes/")
she_ns = Namespace("http://data-iremus.huma-num.fr/ns/sherlock#")

output_graph.bind("crm", crm_ns)
output_graph.bind("dcterms", DCTERMS)
output_graph.bind("lrmoo", lrmoo_ns)
output_graph.bind("sdt", sdt_ns)
output_graph.bind("skos", SKOS)
output_graph.bind("she", she_ns)


# Fonctions
a = RDF.type

def crm(x):
    return URIRef(crm_ns[x])


def lrm(x):
    return URIRef(lrmoo_ns[x])


def she(x):
    return URIRef(iremus_ns[x])


def t(s, p, o):
    output_graph.add((s, p, o))


# Récupération du fichier excel
with xlrd.open_workbook(args.iiif_excel) as wb:
    sheet_coll = wb.sheet_by_index(1)

    collection = she(cache_40CM.get_uuid(["collection", "uuid"], True))
    t(collection, a, crm("D1_Digital_Object"))
    collection_E41 = she(cache_40CM.get_uuid(["collection", "E41"], True))
    t(collection, crm("P1_is_identified_by"), collection_E41)
    t(collection_E41, RDFS.label, Literal(sheet_coll.cell_value(4, 1)))
    t(collection, crm("P2_has_type"), she("14926d58-83e7-4414-90a8-1a3f5ca8fec1"))


# Pour chaque collection, je crée un turtle
## Pour chaque image de la collection, j'ajoute des infos au turtle

output_graph.serialize(destination=args.output_ttl, format="turtle", base="http://data-iremus.huma-num.fr/id/")
cache_40CM.bye()

