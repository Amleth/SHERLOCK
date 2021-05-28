import argparse
from sherlockcachemanagement import Cache
from rdflib import Graph, Namespace, DCTERMS, RDF, RDFS, SKOS, URIRef, XSD, URIRef as u, Literal as l
from openpyxl import load_workbook

# ARGUMENTS
parser = argparse.ArgumentParser()
parser.add_argument("--xls")
parser.add_argument("--ttl")
parser.add_argument("--cache")
args = parser.parse_args()

# CACHE
cache = Cache(args.cache)

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
        if colonne.value != None:
            if colonne.value not in broaders:
                broaders.append(colonne.value)
                broader = broaders[-2:][0]

                # Concepts
                if colonne != row[6] and colonne != row[7]:
                    E55_Type = she(cache.get_uuid(["vocabulaire indexation gravures", broader, colonne.value.lower(), "uuid"], True))
                    t(E55_Type, a, crm("E55_Type"))
                    t(E55_Type, crm("P1_is_identified_by"), l(colonne.value))

                    # Broaders
                    if broader != colonne.value:
                        E55_broader = she(cache.get_uuid(["vocabulaire indexation gravures", broader, broader.lower(), "uuid"], True))
                        t(E55_Type, crm("P127_has_broader_term"), E55_broader)

                # SeeAlso
                if colonne == row[6] or colonne == row[7]:
                    seeAlso = colonne.value

                    # Broaders
                    if broader != seeAlso:
                        E55_broader = she(cache.get_uuid(["vocabulaire indexation gravures", broader, broader.lower(), "uuid"], True))
                        t(E55_broader, RDFS.seeAlso, l(seeAlso))


###########################################################################################################
# CREATION DU FICHIER TURTLE
###########################################################################################################

serialization = g.serialize(format="turtle", base="http://data-iremus.huma-num.fr/id/")
with open(args.ttl, "wb") as f:
    f.write(serialization)

cache.bye()
