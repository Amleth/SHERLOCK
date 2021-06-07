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


#######################################################################################
# RECUPERATION DES DONNEES
#######################################################################################

norm_label_to_entities_registry = {}
entity_to_label_registry = {}
parent_to_children_registry = {}
child_to_parent_registry = {}
entity_to_F34 = {}

# E55, P1 et F34
# TODO: P1 composites

r = requests.get(args.dburi,  params={"query": """
PREFIX crm: <http://www.cidoc-crm.org/cidoc-crm/>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
SELECT *
WHERE {
    GRAPH <http://data-iremus.huma-num.fr/graph/mercure-galant> {
        ?entity rdf:type crm:E55_Type .
        ?entity crm:P1_is_identified_by ?label .
        ?F34 crm:P71_lists ?entity .
    }
}
"""})


for b in r.json()["results"]["bindings"]:
    entity = b["entity"]["value"]
    label = b["label"]["value"]
    F34 = b["F34"]["value"]
    label_norm = normalize_string(label)

    if not label_norm in norm_label_to_entities_registry:
        norm_label_to_entities_registry[label_norm] = []
    norm_label_to_entities_registry[label_norm].append(entity)

    if not entity in entity_to_label_registry:
        entity_to_label_registry[entity] = []
    entity_to_label_registry[entity].append(label)

    if not entity in entity_to_F34:
        entity_to_F34[entity] = []
    entity_to_F34[entity].append(F34)


# E55 & P127

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

#pprint(entity_to_label_registry)
#pprint(parent_to_children_registry)
#pprint(child_to_parent_registry)


#######################################################################################
# CREATION DE L'INDEX
#######################################################################################

def get_ancestors(E55):
    for child, parent in child_to_parent_registry.items():
        if child == E55:
            index[label_norm]["ancestors"][n] = {}
            index[label_norm]["ancestors"][n]["iri"] = parent
            for entity, labels in entity_to_label_registry.items():
                if entity == parent:
                    for parent_label in labels:
                        index[label_norm]["ancestors"][n]["label"] = parent_label

    # n+1
    # get_ancestors(parent)

            for child, ancestor in child_to_parent_registry.items():
                if child == parent:
                    index[label_norm]["ancestors"][2] = {}
                    index[label_norm]["ancestors"][2]["iri"] = ancestor
                    for entity, labels in entity_to_label_registry.items():
                        if entity == ancestor:
                            for ancestor_label in labels:
                                index[label_norm]["ancestors"][2]["label"] = ancestor_label


# le label normalisé de l'entité et ses iris
for label_norm, iris in norm_label_to_entities_registry.items():
    index[label_norm] = {}
    index[label_norm]["iris"] = iris
    index[label_norm]["ancestors"] = {}
    n = 1

    for iri in iris:
        # Le vocabulaire contrôlé listant l'iri
        for entity, F34 in entity_to_F34.items():
            if entity == iri:
                index[label_norm]["F34"] = [string for string in F34]
        get_ancestors(iri)


with open(args.json, 'w', encoding='utf8') as f:
    json.dump(index, f, ensure_ascii=False)