import argparse
import hashlib
import os
from pathlib import Path, PurePath
from types import prepare_class
from rdflib import Graph, Literal, Namespace, DCTERMS, RDF, RDFS, SKOS, URIRef, URIRef as u, Literal as l
import re
import sys
import uuid
import yaml

parser = argparse.ArgumentParser()
parser.add_argument("--inputrdf")
parser.add_argument("--outputttl")
parser.add_argument("--cache_institutions")
args = parser.parse_args()

# CACHE

sys.path.append(str(Path(".").absolute().parent.parent))
from cache_management import get_uuid, read_cache, write_cache  # nopep8

cache_file = str(PurePath.joinpath(Path(".").absolute(), "cache_institutions.yaml"))

# Lecture du cache
cache_des_uuid_du_thesaurus_institutions = None
with open(args.cache_institutions) as f:
    cache_des_uuid_du_thesaurus_institutions = yaml.load(f, Loader=yaml.FullLoader)

################################################################################
# Initialisation des graphes
################################################################################

input_graph = Graph()
input_graph.load(args.inputrdf)

output_graph = Graph()

crm_ns = Namespace("http://www.cidoc-crm.org/cidoc-crm/")
crmdig_ns = Namespace("http://www.ics.forth.gr/isl/CRMdig/")
iremus_ns = Namespace("http://data-iremus.huma-num.fr/id/")
lrmoo_ns = Namespace("http://www.cidoc-crm.org/lrmoo/")
sdt_ns = Namespace("http://data-iremus.huma-num.fr/datatypes/")

output_graph.bind("crm", crm_ns)
output_graph.bind("crmdig", crmdig_ns)
output_graph.bind("dcterms", DCTERMS)
output_graph.bind("lrmoo", lrmoo_ns)
output_graph.bind("sdt", sdt_ns)

a = RDF.type


def crm(x):
    return URIRef(crm_ns[x])


def dig(x):
    return URIRef(crmdig_ns[x])


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

####################################################################################
# Données statiques
####################################################################################

E32_ancien_regime_uri = URIRef(iremus_ns["b18e2fad-4827-4533-946a-1b9914df6e18"])
E32_institutions_uri = URIRef(iremus_ns["8a29e857-3faf-49f1-969b-91572e77218e"])
t(E32_ancien_regime_uri, a, crm("E32_Authority_Document"))
t(E32_ancien_regime_uri, crm("P1_is_identified_by"), Literal("Ancien Régime"))
t(E32_ancien_regime_uri, crm("P71_lists"), E32_institutions_uri)
t(E32_institutions_uri, a, crm("E32_Authority_Document"))
t(E32_institutions_uri, crm("P1_is_identified_by"), Literal("Noms d'institutions et de corporations"))

for opentheso_institution_uri, p, o in input_graph.triples((None, RDF.type, SKOS.Concept)):
    identifier = ro(opentheso_institution_uri, DCTERMS.identifier)
    E74_uri = she(get_uuid(["institutions et corporations", identifier, "uuid"]))
    E41_uri = she(get_uuid(["institutions et corporations", identifier, "E41"]))
    t(E74_uri, a, crm("E74_Group"))
    t(E32_institutions_uri, crm("P71_lists"), E74_uri)
    t(E74_uri, crm("P1_is_identified_by"), E41_uri)
    t(E41_uri, a, crm("E41_Appellation"))
    t(E41_uri, RDFS.label, ro(opentheso_institution_uri, SKOS.prefLabel))
    #altLabels = ro_list(opentheso_personne_uri, SKOS.altLabel)


write_cache(cache_file)
output_graph.serialize(destination=args.outputttl, format="turtle", base="http://data-iremus.huma-num.fr/id/")