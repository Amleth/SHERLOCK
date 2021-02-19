# N'ont pas de prefLabel :
#     http://opentheso3.mom.fr/opentheso3/?idc=examinateur_au_ahatelet&idt=173
#     http://opentheso3.mom.fr/opentheso3/?idc=Orchestre_de_la_Comedie_Francaise&idt=173
# Certains concepts sont liés à plusieurs skos:narrower

import argparse
from pathlib import Path, PurePath
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

parser = argparse.ArgumentParser()
parser.add_argument("--input_rdf")
parser.add_argument("--output_xlsx")
args = parser.parse_args()

g = Graph()
g.load(args.input_rdf)


def get_top_concepts():
    topConcepts = list(
        g.objects(u("http://opentheso3.mom.fr/opentheso3/173"), SKOS.hasTopConcept)
    )
    return topConcepts


def explore_concept(concept, depth=0):
    # Label
    prefLabels = list(g.objects(concept, SKOS.prefLabel))
    if len(prefLabels) == 0:
        return
    print("    " * depth, prefLabels[0])

    # Narrowers
    narrowers = list(g.objects(concept, SKOS.narrower))
    for narrower in narrowers:
        explore_concept(narrower, depth + 1)


for topConcept in get_top_concepts():
    explore_concept(topConcept)