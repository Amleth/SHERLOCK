import argparse
from rdflib.plugins import sparql
from rdflib import (
    Graph,
    Literal,
    Namespace,
    DCTERMS,
    RDF,
    RDFS,
    SKOS,
    URIRef,
    URIRef as u,
    Literal as l,
)
import xlsxwriter

parser = argparse.ArgumentParser()
parser.add_argument("--input_rdf")
args = parser.parse_args()

g = Graph()
g.load(args.input_rdf)


def count_concepts():
    q = g.query(
        """
        SELECT (COUNT(?concept) AS ?n)
        WHERE {
            ?concept <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://www.w3.org/2004/02/skos/core#Concept> .
        }
        """)
    return int(list(q)[0][0])


print(f"{count_concepts()} concepts à traiter")


def print_children(concept, depth=0):
    concept = URIRef(concept)
    q = sparql.prepareQuery("""
    SELECT ?narrower ?narrower_prefLabel ?narrower_id
    WHERE {
        ?concept <http://www.w3.org/2004/02/skos/core#narrower> ?narrower .
        ?narrower <http://purl.org/dc/terms/identifier> ?narrower_id .
        ?narrower <http://www.w3.org/2004/02/skos/core#prefLabel> ?narrower_prefLabel .
    }
    ORDER BY ?narrower_prefLabel
    """)
    for row in g.query(q, initBindings={'concept': concept}):
        print("    " * depth, row[1])
        print("    " * depth, f"••••{row[2]}")
        print_children(row[0], depth + 1)


print_children("https://opentheso3.mom.fr/opentheso3/?idc=chanoines_reguliers&idt=166")
