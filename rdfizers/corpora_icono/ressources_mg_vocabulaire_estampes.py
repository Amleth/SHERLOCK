import argparse
from sherlockcachemanagement import Cache
from rdflib import Graph, Namespace, DCTERMS, RDF, RDFS, SKOS, URIRef, XSD, URIRef as u, Literal as l
from openpyxl import load_workbook
from pprint import pprint
import yaml

# ARGUMENTS
parser = argparse.ArgumentParser()
parser.add_argument("--xls")
parser.add_argument("--ttl")
parser.add_argument("--cache")
parser.add_argument("--cache_applati")
args = parser.parse_args()

# CACHE
cache = Cache(args.cache)
cache_applati = Cache(args.cache_applati)

# INSTANCIATION DU GRAPHE
g = Graph()
iremus_ns = Namespace("http://data-iremus.huma-num.fr/id/")
g.bind("she", iremus_ns)
crm_ns = Namespace("http://www.cidoc-crm.org/cidoc-crm/")
g.bind("crm", crm_ns)
lrmoo_ns = Namespace("http://www.cidoc-crm.org/lrmoo/")
g.bind("lrmoo", lrmoo_ns)


def t(s, p, o):
    g.add((s, p, o))


def she(x):
    return iremus_ns[x]


def crm(x):
    return crm_ns[x]


def lrm(x):
    return lrmoo_ns[x]


a = RDF.type

###########################################################################################################
# CREATION DES DONNEES
###########################################################################################################

# FICHIER EXCEL
fichier_excel = load_workbook(args.xls)
vocab_excel = fichier_excel.active

# TRIPLETS
F34_uuid = she('957985bf-e95a-4e29-b5ad-3520e2eea34e')
g.add((F34_uuid, RDF.type, lrm('F34_Controlled_Vocabulary')))
g.add((F34_uuid, crm('P1_is_identified_by'), l("Vocabulaire d'indexation des gravures du Mercure Galant")))
g.add((F34_uuid, DCTERMS.creator, she('ea287800-4345-4649-af12-7253aa185f3f')))

for row in vocab_excel:

    if row[1].value == "categorie":
        continue

    broaders = []

    for colonne in row:
        if colonne.value != None and colonne != row[6] and colonne != row[7]:
            broaders.append(colonne.value)

    if len(broaders) == 0:
        continue

    broaders = [b.lower() for b in broaders]

    for b in broaders:
        E55_Type = she(cache.get_uuid([*broaders, "uuid"], True))
        t(E55_Type, a, crm("E55_Type"))
        t(E55_Type, crm("P1_is_identified_by"), l(broaders[-1]))
        t(F34_uuid, crm("P71_lists"), E55_Type)

    top_concept = she(cache.get_uuid([broaders[0], "uuid"], True))
    t(F34_uuid, she("sheP_a_pour_entité_de_plus_haut_niveau"), top_concept)

    if len(broaders) >= 2:
        for i in range(1, len(broaders)):
            #print(broaders[:i], broaders[:i+1])
            broader = she(cache.get_uuid([*broaders[:i], "uuid"]))
            narrower = she(cache.get_uuid([*broaders[:i+1], "uuid"]))
            t(narrower, crm("P127_has_broader_term"), broader)

    broader_seeAlso = []

    for colonne in row:
        if colonne.value != None:
            broader_seeAlso.append(colonne.value)
            broader_seeAlso = [b.lower() for b in broader_seeAlso]
            if colonne == row[6] or colonne == row[7]:
                seeAlso = colonne.value
                for i in range(1, len(broader_seeAlso)):
                    #print(broader_seeAlso[:i], broader_seeAlso[:i+1])
                    broader = she(cache.get_uuid([*broader_seeAlso[:i], "uuid"]))
                    t(broader, RDFS.seeAlso, l(seeAlso))


cache.bye()

#Dictionnaire des concepts/uuid sans arborescence, pour l'alignement de l'indexation au vocabulaire
d = {}

with open(args.cache, "r") as f:
    cache_arborescent = yaml.load(f, Loader=yaml.FullLoader)

def label_uuid():
    print(label, items["uuid"])
    d[label] = []
    d[label].append(items["uuid"])
    print(items)
    for key, objets in items:
    #     print(key + ':', objets["uuid"])
    # #     d[key] = []
    # #     d[key].append(items["uuid"])
    #label_uuid()

for label, items in cache_arborescent.items():
        label_uuid()


with open(args.cache_applati, "w", encoding='utf-8') as f:
    yaml.dump(d, f, allow_unicode=True)

###########################################################################################################
# CREATION DU FICHIER TURTLE
###########################################################################################################

serialization = g.serialize(format="turtle", base="http://data-iremus.huma-num.fr/id/")
with open(args.ttl, "wb") as f:
    f.write(serialization)
