import argparse
import json
from pprint import pprint
import requests

parser = argparse.ArgumentParser()
parser.add_argument("--dburi")
parser.add_argument("--json")
args = parser.parse_args()

index = {}


def normalize_string(s):
    s_norm = ''

    for c in s:
        if c.isalnum() == False:
            pass
        elif c in 'âà':
            s_norm += 'a'
        elif c in 'ç':
            s_norm += 'c'
        elif c in 'éèê':
            s_norm += 'e'
        elif c in 'öô':
            s_norm += 'o'
        elif c == 'œ':
            s_norm += 'o'
            s_norm += 'e'
        else:
            s_norm += c

    return s_norm.lower()


norm_label_to_entities_registry = {}
entity_to_label_registry = {}
parent_to_children_registry = {}
child_to_parent_registry = {}

#
# E55 & P1
# TODO: P1 composites
#

r = requests.get(args.dburi,  params={"query": """
PREFIX crm: <http://www.cidoc-crm.org/cidoc-crm/>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
SELECT *
WHERE {
    GRAPH <http://data-iremus.huma-num.fr/graph/mercure-galant> {
        ?entity rdf:type crm:E55_Type .
        ?entity crm:P1_is_identified_by ?label .
  }
}
"""})

for b in r.json()["results"]["bindings"]:
    entity = b["entity"]["value"]
    label = b["label"]["value"]
    label_norm = normalize_string(label)

    if not label_norm in norm_label_to_entities_registry:
        norm_label_to_entities_registry[label_norm] = []
    norm_label_to_entities_registry[label_norm].append(entity)

    if not entity in entity_to_label_registry:
        entity_to_label_registry[entity] = []
    entity_to_label_registry[entity].append(label)

#
# E55 & P127
#

r = requests.get(args.dburi,  params={"query": """
PREFIX crm: <http://www.cidoc-crm.org/cidoc-crm/>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
SELECT *
WHERE {
    GRAPH <http://data-iremus.huma-num.fr/graph/mercure-galant> {
        ?entity rdf:type crm:E55_Type .
        ?broader rdf:type crm:E55_Type .
        ?entity crm:P127_has_broader_term ?broader .
  }
}
"""})

for b in r.json()["results"]["bindings"]:
    child = b["entity"]["value"]
    parent = b["broader"]["value"]

    if parent not in parent_to_children_registry:
        parent_to_children_registry[parent] = []
    parent_to_children_registry[parent].append(child)

    child_to_parent_registry[child] = parent

#
# CONSTRUCTION DE L'INDEX
#

# viesociale:
#     iris:
#         - http://data-iremus.huma-num.fr/id/7358d9b7-7ab1-42e1-88f0-c3d4e3e75be2
#         - http://data-iremus.huma-num.fr/id/fdf6643e-3359-4000-b40a-0b2f26db7459
#     f34:
#         iri: <...>
#         label: "..."
#     ancestors:
#       - iri: <...>
#         label: "..."
#       - iri: <...>
#         label: "..."
#       - iri: <...>
#         label: "..."

with open(args.json, 'w') as f:
    json.dump(index, f)
