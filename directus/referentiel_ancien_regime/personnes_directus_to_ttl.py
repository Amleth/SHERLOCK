import json
from rdflib import Graph, Literal, Namespace, DCTERMS, RDF, RDFS, SKOS, URIRef, URIRef as u, Literal as l
import argparse
from pprint import pprint
from sherlockcachemanagement import Cache

# Arguments
parser = argparse.ArgumentParser()
parser.add_argument("--json")
parser.add_argument("--ttl")
parser.add_argument("--cache")
args = parser.parse_args()

# Cache
cache = Cache(args.cache)

############################################################################################
## INITIALISATION DU GRAPHE ET NAMESPACES
############################################################################################

output_graph = Graph()

crm_ns = Namespace("http://www.cidoc-crm.org/cidoc-crm/")
iremus_ns = Namespace("http://data-iremus.huma-num.fr/id/")
sdt_ns = Namespace("http://data-iremus.huma-num.fr/datatypes/")
sherlock_ns = Namespace("http://data-iremus.huma-num.fr/ns/sherlock#")

output_graph.bind("crm", crm_ns)
output_graph.bind("dcterms", DCTERMS)
output_graph.bind("skos", SKOS)
output_graph.bind("sdt", sdt_ns)
output_graph.bind("she_ns", sherlock_ns)

a = RDF.type

def crm(x):
	return URIRef(crm_ns[x])

def she(x):
	return URIRef(iremus_ns[x])

def she_ns(x):
	return URIRef(sherlock_ns[x])

def t(s, p, o):
	output_graph.add((s, p, o))


############################################################################################
## RECUPERATION DES DONNEES
############################################################################################

E32_personnes_uri = u(iremus_ns["947a38f0-34ac-4c54-aeb7-69c5f29e77c0"])
t(E32_personnes_uri, a, crm("E32_Authority_Document"))
t(E32_personnes_uri, crm("P1_is_identified_by"), l("Noms de personnes"))

with open(args.json) as f:
	json_file = json.load(f)

	for personne in json_file["data"]["personnes"]:
		E21_uuid = personne["id"]
		E21_uri = she(E21_uuid)
		t(E21_uri, a, crm("E21_Person"))
		t(E32_personnes_uri, crm("P71_lists"), E21_uri)

		# PrefLabel
		E41_uri = she(cache.get_uuid(["personnes", E21_uri, "E41"], True))
		t(E21_uri, crm("P1_is_identified_by"), E41_uri)
		t(E41_uri, a, crm("E41_Appellation"))
		t(E41_uri, RDFS.label, l(personne["label"]))
		t(E41_uri, crm("P2_has_type"), SKOS.prefLabel)

		# AltLabels
		n = 1
		clé = "alt_label_" + str(n)
		while clé in personne.keys():
			altlabel = personne[clé]
			if altlabel != None:
				E41_alt_uri = she(cache.get_uuid(["personnes", E21_uri, "E41 alt", altlabel], True))
				t(E41_alt_uri, a, crm("E41_Appellation"))
				t(E41_alt_uri, RDFS.label, l(altlabel))
				t(E21_uri, crm("P1_is_identified_by"), E41_alt_uri)
				t(E41_alt_uri, crm("P2_has_type"), SKOS.altLabel)
			n += 1
			clé = "alt_label_" + str(n)

		# TODO Ajouter les dcterms:created du fichier skos pour dater les E13 ?

		# Définition
		if personne["definition"] != None:
			E13_definition_uri = she(cache.get_uuid(["personnes", E21_uri, "definition", "E13"], True))
			t(E13_definition_uri, a, crm("E13_Attribute_Assignement"))
			t(E13_definition_uri, crm("P14_carried_out_by"), she("684b4c1a-be76-474c-810e-0f5984b47921"))
			t(E13_definition_uri, crm("P140_assigned_attribute_to"), E21_uri)
			t(E13_definition_uri, crm("P141_assigned"), l(personne["definition"]))
			t(E13_definition_uri, crm("P177_assigned_property_type"), she_ns("P3_definition"))

		# Note historique
		if personne["note_historique"] != None:
			E13_note_uri = she(cache.get_uuid(["personnes", E21_uri, "note historique", "E13"], True))
			t(E13_note_uri, a, crm("E13_Attribute_Assignement"))
			t(E13_note_uri, crm("P14_carried_out_by"), she("684b4c1a-be76-474c-810e-0f5984b47921"))
			t(E13_note_uri, crm("P140_assigned_attribute_to"), E21_uri)
			t(E13_note_uri, crm("P141_assigned"), l(personne["note_historique"]))
			t(E13_note_uri, crm("P177_assigned_property_type"), crm("P3_has_note"))

		# Identifant IReMus
		if personne["ref_iremus"] != None:
			t(E21_uri, crm("P1_is_identified_by"), l(personne["ref_iremus"]))

		# Identifiant Hortus
		if personne["ref_hortus"] != None:
			t(E21_uri, crm("P1_is_identified_by"), l(personne["ref_hortus"]))


############################################################################################
## SERIALISATION DU GRAPHE
############################################################################################

serialization = output_graph.serialize(format="turtle", base="http://data-iremus.huma-num.fr/id/")
with open(args.ttl, "wb") as f:
	f.write(serialization)

cache.bye()