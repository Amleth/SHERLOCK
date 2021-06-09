import argparse
from openpyxl import load_workbook
import sys
# sys.path.insert(0, '/rdfizers/helpers')
# import helpers_rdf.py
# from ..rdfizers import *
# from helpers_rdf import init_graph
from sherlockcachemanagement import Cache
from rdflib import DCTERMS, Graph, Namespace, RDF, SKOS

######################################################################################
# CACHES
######################################################################################

parser = argparse.ArgumentParser()
parser.add_argument("--xlsx")
parser.add_argument("--ttl")
parser.add_argument("--cache")
parser.add_argument("--cache_corpus")
args = parser.parse_args()

cache = Cache(args.cache)
cache_corpus = Cache(args.cache_corpus)

######################################################################################
# CACHES
######################################################################################

g = Graph()

crm_ns = Namespace("http://www.cidoc-crm.org/cidoc-crm/")
crmdig_ns = Namespace("http://www.ics.forth.gr/isl/CRMdig/")
iremus_ns = Namespace("http://data-iremus.huma-num.fr/id/")
lrmoo_ns = Namespace("http://www.cidoc-crm.org/lrmoo/")
sdt_ns = Namespace("http://data-iremus.huma-num.fr/datatypes/")
sherlock_ns = Namespace("http://data-iremus.huma-num.fr/ns/sherlock#")

g.bind("crm", crm_ns)
g.bind("dcterms", DCTERMS)
g.bind("lrm", lrmoo_ns)
g.bind("sdt", sdt_ns)
g.bind("skos", SKOS)
g.bind("crmdig", crmdig_ns)
g.bind("she_ns", sherlock_ns)
g.bind("she", iremus_ns)

######################################################################################
# FONCTIONS RDF
######################################################################################

a = RDF.type

def crm(x):
    return crm_ns[x]

def crmdig(x):
    return crmdig_ns[x]

def lrm(x):
    return lrmoo_ns[x]

def she(x):
    return iremus_ns[x]

def she_ns(x):
    return sherlock_ns[x]

def t(s, p, o):
    g.add((s, p, o))


#######################################################################################
# RECUPERATION DES DONNEES
#######################################################################################

# Fichier Excel
sheet = load_workbook(args.xlsx).active

for row in sheet.iter_rows(min_row=2):
    valeur = row[0].value
    print(valeur)


#######################################################################################
# CREATION DU GRAPHE ET DU CACHE
#######################################################################################

cache.bye()

serialization = g.serialize(format="turtle", base="http://data-iremus.huma-num.fr/id/")
with open(args.ttl, "wb") as f:
	f.write(serialization)

