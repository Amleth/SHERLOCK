# Demandes de corrections :
# EM -> EP
# PS -> TS

# EP employé pour => synonymes -> crm:P139_has_alternative_form
# NA Note d'application -> crm:P3_has_note
# TG terme générique

import argparse
from openpyxl import load_workbook
from rdflib import Graph, Literal, Namespace, DCTERMS, RDF, RDFS, SKOS, URIRef, XSD, URIRef as u, Literal as l
import sys
from sherlockcachemanagement import Cache

parser = argparse.ArgumentParser()
parser.add_argument("--txt")
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
sherlock = Namespace("http://data-iremus.huma-num.fr/ns/")
g.bind("sherlock", sherlock)

F34_uuid = iremus['44615793-155a-4439-bb0e-5d26c08089f2']

g.add((F34_uuid, RDF.type, lrmoo['F34_Controlled_Vocabulary']))
g.add((F34_uuid, crm['P1_is_identified_by'], l('Thésaurus des mots-clefs du Mercure Galant')))

lines = []

with open(args.txt, "r") as f:
    lines = f.readlines()

toplevel_keywords = []
current_broaders = {}

last_depth = 0
for line in lines:
    line = line.rstrip()
    depth = len([_ for _ in line.split('    ') if _ == ''])

    # clean up
    if depth <= last_depth:
        k_to_kill = []
        for k, v in current_broaders.items():
            if k >= depth:
                k_to_kill.append(k)
        for k in k_to_kill:
            del current_broaders[k]

    print(line, depth, current_broaders)

    line = line.strip()
    if depth - 1 >= 0:
        if line[0:3] == 'TS ':
            line = line[3:]
            g.add((
                u(cache.get_uuid([line], True)),
                RDF.type,
                crm['E55_Type']
            ))
            g.add((
                u(cache.get_uuid([line])),
                crm['P127_has_broader_term'],
                u(cache.get_uuid([current_broaders[depth - 1]]))
            ))
            g.add((
                u(cache.get_uuid([line], True)),
                crm['P1_is_identified_by'],
                l(line)
            ))
            g.add((
                F34_uuid,
                crm['P71_lists'],
                u(cache.get_uuid([line]))
            ))
        elif line[0:3] == 'EP ':
            line = line[3:]
            g.add((
                u(cache.get_uuid([current_broaders[depth - 1]])),
                crm['P139_has_alternative_form'],
                l(line)
            ))
        elif line[0:3] == 'NA ':
            line = line[3:]
            g.add((
                u(cache.get_uuid([current_broaders[depth - 1]])),
                crm['P3_has_note'],
                l(line)
            ))
        elif line[0:3] == 'TG ':
            line = line[3:]
            toplevel_keywords.remove(current_broaders[depth - 1])
            g.add((
                u(cache.get_uuid([current_broaders[depth - 1]])),
                crm['P127_has_broader_term'],
                u(cache.get_uuid([line], True))
            ))
        else:
            print("Code pourri :", line)
    else:
        g.add((
            u(cache.get_uuid([line], True)),
            RDF.type,
            crm['E55_Type']
        ))
        g.add((
            u(cache.get_uuid([line], True)),
            crm['P1_is_identified_by'],
            l(line)
        ))
        g.add((
            F34_uuid,
            crm['P71_lists'],
            u(cache.get_uuid([line]))
        ))
        toplevel_keywords.append(line)

    current_broaders[depth] = line.strip()
    last_depth = depth

for tlkw in toplevel_keywords:
    g.add((F34_uuid, sherlock['sheP_a_pour_entité_de_plus_haut_niveau'], u(cache.get_uuid([tlkw]))))

serialization = g.serialize(format="turtle", base="http://data-iremus.huma-num.fr/id/")
with open(args.ttl, "wb") as f:
    f.write(serialization)

cache.bye()
