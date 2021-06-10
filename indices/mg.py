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
        elif c in 'ÀÁÂÃÄÅàáâãäå':
            s_norm += 'a'
        elif c in 'Çç':
            s_norm += 'c'
        elif c in 'ÈÉÊËèéêë':
            s_norm += 'e'
        elif c in 'ÒÓÔÕÖØòóôõöø':
            s_norm += 'o'
        elif c in 'ÌÍÎÏìíîï':
            s_norm += 'i'
        elif c in 'ÙÚÛÜùúûü':
            s_norm += 'u'
        elif c in 'ÿ':
            s_norm += 'y'
        elif c in 'Ññ':
            s_norm += 'n'
        elif c == 'œ':
            s_norm += 'o'
            s_norm += 'e'
        elif c == 'ß':
            s_norm += 'ss'
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
        entity_to_F34[entity] = F34


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
    for entity in entity_to_label_registry:
        if entity not in child_to_parent_registry:
            child_to_parent_registry[entity] = None

# pprint(entity_to_label_registry)
# pprint(parent_to_children_registry)
# pprint(child_to_parent_registry)


#######################################################################################
# CREATION DE L'INDEX
#######################################################################################

# le label normalisé de l'entité
for label_norm, iris in norm_label_to_entities_registry.items():
    index[label_norm] = {}
    index[label_norm]["iris"] = {}


    for iri in iris:

        for entity, labels in entity_to_label_registry.items():
            if entity == iri:
                for label in labels:
                    index[label_norm]["label"] = label

        index[label_norm]["iris"][iri] = {}
        index[label_norm]["iris"][iri]["ancestors"] = {}

        # F34 Controlled Vocabulary
        for entity, F34 in entity_to_F34.items():
            if entity == iri:
                index[label_norm]["iris"][iri]["F34"] = F34

        # Ancêtres
        parent_iri = child_to_parent_registry[iri]

        # if parent_iri:
            # index[label_norm]["iris"][iri]["ancestors"]["iri"] = []
            # index[label_norm]["iris"][iri]["ancestors"]["label"] = []

        while parent_iri:
            index[label_norm]["iris"][iri]["ancestors"]["iri"] = parent_iri
            for entity, labels in entity_to_label_registry.items():
                if entity == parent_iri:
                    for parent_label in labels:
                        index[label_norm]["iris"][iri]["ancestors"]["label"] = parent_label
            parent_iri = child_to_parent_registry[parent_iri]


with open(args.json, 'w', encoding='utf8') as f:
    json.dump(index, f, ensure_ascii=False)
