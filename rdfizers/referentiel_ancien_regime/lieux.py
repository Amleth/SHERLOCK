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
from sherlockcachemanagement import Cache

parser = argparse.ArgumentParser()
parser.add_argument("--inputrdf")
parser.add_argument("--outputttl")
parser.add_argument("--cache_lieux")
parser.add_argument("--cache_corpus")
args = parser.parse_args()

# CACHE

cache_corpus = Cache(args.cache_corpus)
cache_lieux = Cache(args.cache_lieux)

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


def explore(id, depth):
	# print("    "*depth, prefLabel, id)

	# E93 Presence
	identifier = ro(id, DCTERMS.identifier)
	if identifier != "https://opentheso3.mom.fr/opentheso3/?idc=1336&idt=43":
		E93_uri = she(cache_lieux.get_uuid(["lieu", identifier, "E93", "uuid"], True))
		t(E93_uri, a, crm("E93_Presence"))
		t(E32_grand_siecle_uri, crm("P71_lists"), E93_uri)


		# DCTERMS.created/modified
		t(E93_uri, DCTERMS.created, ro(id, DCTERMS.created))
		t(E93_uri, DCTERMS.modified, ro(id, DCTERMS.modified))


		# E41_Appellation
		E41_uri = she(cache_lieux.get_uuid(["lieu", identifier, "E93", "E41"], True))
		t(E93_uri, crm("P1_is_identified_by"), E41_uri)
		t(E41_uri, a, crm("E41_Appellation"))
		for prefLabel in ro_list(id, SKOS.prefLabel):
			t(E41_uri, RDFS.label, prefLabel)
		altLabels = ro_list(id, SKOS.altLabel)
		if len(altLabels) > 0:
			for altLabel in altLabels:
				E41_alt_uri = she(cache_lieux.get_uuid(["lieu", identifier, "E93", "E41_alt", altLabel], True))
				t(E41_alt_uri, a, crm("E41_Appellation"))
				t(E41_alt_uri, RDFS.label, altLabel)
				t(E41_uri, crm("P139_has_alternative_form"), E41_alt_uri)


		# E13 Indexation
		def process_note(p):
			values = ro_list(id, p)
			for v in values:
				if "##id##" in v:
					v = v.split("##id##")
					for v in v:
						if v:
							m = re.search(indexation_regexp, v)
							m_livraison = re.search(indexation_regexp_livraison, v)
							if m:
								clef_mercure_livraison = m_livraison.group()
								clef_mercure_article = m.group()
								try:
									F2_article_uri = she(cache_corpus.get_uuid(
										["Corpus", "Livraisons", clef_mercure_livraison, "Expression TEI", "Articles",
										 clef_mercure_article, "F2"]))
									E13_index_uri = she(cache_lieux.get_uuid(["lieu", identifier, "E93", "E13_indexation"], True))
									t(E13_index_uri, a, crm("E13_Attribute_Assignement"))
									t(E13_index_uri, DCTERMS.created, ro(id, DCTERMS.created))
									t(E13_index_uri, crm("P14_carried_out_by"),
									  she("899e29f6-43d7-4a98-8c39-229bb20d23b2"))
									t(E13_index_uri, crm("P14_carried_out_by"),
									  she("82476bac-cd8a-4bdc-a695-cf90444c9432"))
									t(E13_index_uri, crm("P140_assigned_attribute_to"), F2_article_uri)
									t(E13_index_uri, crm("P141_assigned"), E93_uri)
									t(E13_index_uri, crm("P177_assigned_property_type"),
									  she("c605c8bb-9387-4da1-baec-b0514fd9999c"))

								except:
									# print(identifier, clef_mercure_article)
									pass


				elif "##" in v:
					v = v.split("##")
					for v in v:
						if v:
							m = re.search(indexation_regexp, v)
							m_livraison = re.search(indexation_regexp_livraison, v)
							if m:
								clef_mercure_livraison = m_livraison.group()
								clef_mercure_article = m.group()
								try:
									F2_article_uri = she(cache_corpus.get_uuid(
										["Corpus", "Livraisons", clef_mercure_livraison, "Expression TEI", "Articles",
										 clef_mercure_article, "F2"]))
									E13_index_uri = she(
										cache_lieux.get_uuid(["lieu", identifier, "E93", "E13_indexation"], True))
									t(E13_index_uri, a, crm("E13_Attribute_Assignement"))
									t(E13_index_uri, DCTERMS.created, ro(id, DCTERMS.created))
									t(E13_index_uri, crm("P14_carried_out_by"),
									  she("899e29f6-43d7-4a98-8c39-229bb20d23b2"))
									t(E13_index_uri, crm("P14_carried_out_by"),
									  she("82476bac-cd8a-4bdc-a695-cf90444c9432"))
									t(E13_index_uri, crm("P140_assigned_attribute_to"), F2_article_uri)
									t(E13_index_uri, crm("P141_assigned"), E93_uri)
									t(E13_index_uri, crm("P177_assigned_property_type"),
									  she("c605c8bb-9387-4da1-baec-b0514fd9999c"))

								except:
									# print(identifier, clef_mercure_article)
									pass

				else:
					note_sha1_object = hashlib.sha1(v.encode())
					note_sha1 = note_sha1_object.hexdigest()
					E13_uri = she(cache_lieux.get_uuid(["lieu", identifier, "E93", "E13"], True))
					t(E13_uri, a, crm("E13_Attribute_Assignement"))
					t(E13_uri, DCTERMS.created, ro(id, DCTERMS.created))
					t(E13_uri, crm("P14_carried_out_by"), she("899e29f6-43d7-4a98-8c39-229bb20d23b2"))
					t(E13_uri, crm("P14_carried_out_by"),
					  she("82476bac-cd8a-4bdc-a695-cf90444c9432"))
					t(E13_uri, crm("P140_assigned_attribute_to"), E93_uri)
					E13_notes_uri = she(cache_lieux.get_uuid(["lieu", identifier, "E93", "E13_notes", note_sha1], True))
					t(E13_notes_uri, RDFS.label, Literal(v))
					t(E13_uri, crm("P141_assigned"), E13_notes_uri)
					t(E13_uri, crm("P177_assigned_property_type"), crm("P3_has_note"))

		for note in [SKOS.note, SKOS.historyNote]:
			process_note(note)


		# Exact et Close Matches
		exactMatches = ro_list(id, SKOS.exactMatch)
		for exactMatch in exactMatches:
			if exactMatch == "https://opentheso3.mom.fr/opentheso3/index.xhtml":
				continue
			t(E93_uri, SKOS.exactMatch, exactMatch)

		closeMatches = ro_list(id, SKOS.closeMatch)
		for closeMatch in closeMatches:
			t(E93_uri, SKOS.closeMatch, closeMatch)


		# Coordonnées géographiques
		E53_uri = she(cache_lieux.get_uuid(["lieu", identifier, "E93", "E53"], True))
		t(E93_uri, crm("P161_has_spatial_projection"), E53_uri)

		geolat = ro(id, URIRef("http://www.w3.org/2003/01/geo/wgs84_pos#lat"))
		geolong = ro(id, URIRef("http://www.w3.org/2003/01/geo/wgs84_pos#long"))
		if geolat and geolong:
			t(E53_uri, crm("P168_place_is_defined_by"), l(f"[{str(geolat)}, {str(geolong)}]"))


	# narrowers
	narrowers = ro_list(id, SKOS.narrower)

	for narrower in narrowers:

		if identifier != "https://opentheso3.mom.fr/opentheso3/?idc=1336&idt=43":


			# P10 falls within
			identifier_n = ro(narrower, DCTERMS.identifier)
			narrower_uuid = she(cache_lieux.get_uuid(["lieu", identifier_n, "E93", "uuid"], True))
			t(narrower_uuid, crm("P10_falls_within"), E93_uri)
		explore(narrower, depth + 1)


####################################################################################
# DONNÉES STATIQUES
####################################################################################

indexation_regexp = r"MG-[0-9]{4}-[0-9]{2}[a-zA-Z]?_[0-9]{1,3}"
indexation_regexp_livraison = r"MG-[0-9]{4}-[0-9]{2}[a-zA-Z]?"

# Création des thésaurus "Ancien Régime" et "Noms de lieux"

E32_ancien_regime_uri = URIRef(iremus_ns["b18e2fad-4827-4533-946a-1b9914df6e18"])
E32_lieux_uri = URIRef(iremus_ns["4e7cdc71-b834-412a-8cab-daa363a8334e"])
t(E32_ancien_regime_uri, a, crm("E32_Authority_Document"))
t(E32_ancien_regime_uri, crm("P1_is_identified_by"), Literal("Ancien Régime"))
t(E32_ancien_regime_uri, crm("P71_lists"), E32_lieux_uri)
t(E32_lieux_uri, a, crm("E32_Authority_Document"))
t(E32_lieux_uri, crm("P1_is_identified_by"), Literal("Noms de lieux"))


####################################################################################
# THESAURUS "GRAND SIECLE"
####################################################################################

# Création du thésaurus "Grand Siècle"

E32_grand_siecle_uri = URIRef(iremus_ns["78061430-df57-4874-8334-44ed215a112e"])
t(E32_grand_siecle_uri, a, crm("E32_Authority_Document"))
t(E32_grand_siecle_uri, crm("P1_is_identified_by"), Literal("Grand Siècle"))
t(E32_lieux_uri, crm("P71_lists"), E32_grand_siecle_uri)

explore(URIRef("https://opentheso3.mom.fr/opentheso3/?idc=1336&idt=43"), 0)


####################################################################################
# THESAURUS "MONDE CONTEMPORAIN"
####################################################################################

# Création du thésaurus "Monde Contemporain"

E32_mon_cont_uri = URIRef(iremus_ns["41dd59e3-2f0c-4ef3-b08c-9606f33a4a48"])
t(E32_mon_cont_uri, a, crm("E32_Authority_Document"))
t(E32_mon_cont_uri, crm("P1_is_identified_by"), Literal("Monde contemporain"))
t(E32_lieux_uri, crm("P71_lists"), E32_mon_cont_uri)

explore(URIRef("https://opentheso3.mom.fr/opentheso3/?idc=275949&idt=43"), 0)


####################################################################################
# ECRITURE DU CACHE ET DES TRIPLETS
####################################################################################

output_graph.serialize(destination=args.outputttl, format="turtle", base="http://data-iremus.huma-num.fr/id/")
cache_corpus.bye()
cache_lieux.bye()