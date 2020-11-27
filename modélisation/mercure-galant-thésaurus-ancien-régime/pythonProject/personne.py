import argparse
import os
from rdflib import Graph, Literal, Namespace, RDF, RDFS, URIRef
import re
import uuid

parser = argparse.ArgumentParser()
parser.add_argument("--rdf")  # Je m'attends à trouver tel argument
parser.add_argument("--ttl")  # Je m'attends à trouver tel argument
args = parser.parse_args()  # Où sont stockés tous les paramètres passés en ligne de commande

################################################################################
# Initialisation du graph
################################################################################

g_pers = Graph()
g_pers.load(args.rdf)

# LE FICHIER EXEMPLE EST PROVISOIRE, IL SERA REMPLACE LORSQUE JE RECEVRAI MES IDENTIFIANTS OPENTHESO ET POURRAI EXPORTER LE BON FICHIER

# Namespaces pour préfixage
sdt_ns = Namespace("http://data-iremus.huma-num.fr/datatypes/")
g_pers.bind("sdt", sdt_ns)
crm_ns = Namespace("http://www.cidoc-crm.org/cidoc-crm/")
g_pers.bind("crm", crm_ns)
crmdig_ns = Namespace("http://www.ics.forth.gr/isl/CRMdig/")
g_pers.bind("crmdig", crmdig_ns)
lrmoo_ns = Namespace("http://www.cidoc-crm.org/lrmoo/")
g_pers.bind("lrmoo", lrmoo_ns)

# Helpers
iremus_ns = Namespace("http://data-iremus.huma-num.fr/id/")

####################################################################################
## Données statiques
####################################################################################

for core_concept in g_pers:
    personne = URIRef(iremus_ns[str(uuid.uuid4())])
    g_pers.add((personne, RDF.type, URIRef(crm_ns["E21_Person"])))

####################################################################################
## Noms
####################################################################################

    for s, p, o in g_pers.triples((None, URIRef("http://www.w3.org/2004/02/skos/core#prefLabel"), None)):
        # prefLabel
        D21_uri = URIRef(iremus_ns[str(uuid.uuid4())])
        g_pers.add((D21_uri, RDF.type, URIRef(crmdig_ns["D21_Person_Name"])))
        g_pers.add((D21_uri, RDFS.label, Literal(o)))
        ## Attribution du nom
        E13_uri = URIRef(iremus_ns[str(uuid.uuid4())])
        g_pers.add((E13_uri, RDF.type, URIRef(crm_ns["E13_Attribute_Assignement"])))
        g_pers.add((E13_uri, URIRef(crm_ns["P14_carried_out_by"]), URIRef(iremus_ns["899e29f6-43d7-4a98-8c39-229bb20d23b2"])))
        g_pers.add((E13_uri, URIRef(crm_ns["P141_assigned"]), D21_uri))
        g_pers.add((E13_uri, URIRef(crm_ns["P177_assigned_property_type"]), URIRef(iremus_ns["4a673f92-174e-41cb-b0e1-9c32985fa07c"]))) #Identification
        g_pers.add((E13_uri, URIRef(crm_ns["P140_assigned_attribute_to"]), personne))
        if (s, "dcterms:created", o) in g_pers:
            g_pers.add((E13_uri, URIRef(crm_ns["P4_has_time-span"]), Literal(o)))

        # altLabel
    for s, p, o in g_pers.triples((None, URIRef("http://www.w3.org/2004/02/skos/core#altLabel"), None)):
        D21_uri = URIRef(iremus_ns[str(uuid.uuid4())])
        g_pers.add((D21_uri, RDFS.label, Literal(o)))
        ## Attribution du nom



turtle = g_pers.serialize(format="turtle", base="http://data-iremus.huma-num.fr/id/").decode("utf-8")
print(turtle)