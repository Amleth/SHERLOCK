import argparse
from rdflib.plugins import sparql
from rdflib import Graph, Literal, Namespace, DCTERMS, RDF, RDFS, SKOS, URIRef, URIRef as u, Literal as l
import xlsxwriter
import uuid
import yaml
from sherlockcachemanagement import Cache

parser = argparse.ArgumentParser()
parser.add_argument("--input_rdf")
parser.add_argument("--output_ttl")
parser.add_argument("--cache_congregations")
parser.add_argument("--cache_corpus")
args = parser.parse_args()

# CACHE

cache_corpus = Cache(args.cache_corpus)
cache_congregations = Cache(args.cache_congregations)

##################################################################################
## INITIALISATION DES GRAPHES
##################################################################################

input_graph = Graph()
input_graph.load(args.input_rdf)

output_graph = Graph()

crm_ns = Namespace("http://www.cidoc-crm.org/cidoc-crm/")
iremus_ns = Namespace("http://data-iremus.huma-num.fr/id/")
lrmoo_ns = Namespace("http://www.cidoc-crm.org/lrmoo/")
sdt_ns = Namespace("http://data-iremus.huma-num.fr/datatypes/")

output_graph.bind("crm", crm_ns)
output_graph.bind("dcterms", DCTERMS)
output_graph.bind("lrmoo", lrmoo_ns)
output_graph.bind("sdt", sdt_ns)
output_graph.bind("skos", SKOS)

a = RDF.type

def crm(x):
    return URIRef(crm_ns[x])


def lrm(x):
    return URIRef(lrmoo_ns[x])


def she(x):
    return URIRef(iremus_ns[x])


def t(s, p, o):
    output_graph.add((s, p, o))


def ro(s, p):
    try:
        return list(input_graph.objects(s, p))[0]
    except:
        return None


def ro_list(s, p):
    try:
        return list(input_graph.objects(s, p))
    except:
        return None


def count_concepts():
    q = g.query(
        """
        SELECT (COUNT(?concept) AS ?n)
        WHERE {
            ?concept <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://www.w3.org/2004/02/skos/core#Concept> .
        }
        """)
    return int(list(q)[0][0])


#print(f"{count_concepts()} concepts à traiter")

# NE PAS OUBLIER E32 THESAURUS

def print_children(concept, depth):
    concept_id = ro(concept, DCTERMS.identifier)
    E74_uri = she(cache_congregations.get_uuid(["congrégations religieuses", concept_id, "uuid"], True))

    #Appellation
    E41_uri = she(cache_congregations.get_uuid(["congrégations religieuses", concept_id, "E41"], True))
    t(E74_uri, crm("P1_is_identified_by"), E41_uri)
    t(E41_uri, a, crm("E41_Appellation"))
    t(E41_uri, RDFS.label, ro(concept, SKOS.prefLabel))

    q = sparql.prepareQuery("""
    SELECT ?narrower ?narrower_prefLabel ?narrower_id
    WHERE {
        ?concept <http://www.w3.org/2004/02/skos/core#narrower> ?narrower .
        ?narrower <http://purl.org/dc/terms/identifier> ?narrower_id .
        ?narrower <http://www.w3.org/2004/02/skos/core#prefLabel> ?narrower_prefLabel .
    }
    ORDER BY ?narrower_prefLabel
    """)

    for row in input_graph.query(q, initBindings={'concept': concept}):

        E74_narrower_uri = she(cache_congregations.get_uuid(["congrégations religieuses", row[2], "uuid"], True))
        t(E74_uri, crm("P107_has_current_or_former_member"), E74_narrower_uri)

        print_children(row[0], depth + 1)

      # SOUCI DE CACHE A GERER

####################################################################################
# DONNEES
####################################################################################

print_children(URIRef("https://opentheso3.mom.fr/opentheso3/?idc=clerge_regulier&idt=166"), 0)

print_children("https://opentheso3.mom.fr/opentheso3/?idc=clerge_seculier&idt=166", 0)

print_children("https://opentheso3.mom.fr/opentheso3/?idc=papaute&idt=166", 0)


output_graph.serialize(destination=args.output_ttl, format="turtle", base="http://data-iremus.huma-num.fr/id/")
cache_corpus.bye()
cache_congregations.bye()

