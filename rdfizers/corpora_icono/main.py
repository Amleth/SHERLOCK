# TODO Transformer les auteurs d'ouvrages en E21?

import argparse
from openpyxl import load_workbook
from rdflib import Graph, Namespace, DCTERMS, RDF, RDFS, SKOS, URIRef as u, XSD, Literal as l
import sys
from sherlockcachemanagement import Cache

# Arguments
parser = argparse.ArgumentParser()
parser.add_argument("--collection_id")
parser.add_argument("--excel_coll")
parser.add_argument("--excel_index")
parser.add_argument("--output_ttl")
parser.add_argument("--cache_40CM")
parser.add_argument("--cache_corpus")
args = parser.parse_args()

# Caches
cache_40CM = Cache(args.cache_40CM)
cache_corpus = Cache(args.cache_corpus)

# Initialisation du graphe
output_graph = Graph()

# Namespaces
crm_ns = Namespace("http://www.cidoc-crm.org/cidoc-crm/")
crmdig_ns = Namespace("http://www.ics.forth.gr/isl/CRMdig/")
iremus_ns = Namespace("http://data-iremus.huma-num.fr/id/")
lrmoo_ns = Namespace("http://www.cidoc-crm.org/lrmoo/")
sdt_ns = Namespace("http://data-iremus.huma-num.fr/datatypes/")
sherlock_ns = Namespace("http://data-iremus.huma-num.fr/ns/sherlock#")

output_graph.bind("crm", crm_ns)
output_graph.bind("dcterms", DCTERMS)
output_graph.bind("lrm", lrmoo_ns)
output_graph.bind("sdt", sdt_ns)
output_graph.bind("skos", SKOS)
output_graph.bind("she", sherlock_ns)
output_graph.bind("crmdig", crmdig_ns)

# Fonctions
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
	output_graph.add((s, p, o))


# Fichiers Excel
# Index des collections
wb_index = load_workbook(args.excel_index)
index = wb_index.active
# Images de la collection
wb_img = load_workbook(args.excel_coll)
img = wb_img.active

#####################################################################
# LA COLLECTION
#####################################################################

collection_row = None

for row in index:
	if row[0].value == args.collection_id:
		collection_row = row
		break

collection = she(cache_40CM.get_uuid(["collection", "uuid"], True))
t(collection, a, crmdig("D1_Digital_Object"))
# Appellation
collection_E41 = she(cache_40CM.get_uuid(["collection", "E41"], True))
t(collection_E41, a, crm("E41_Appellation"))
t(collection, crm("P1_is_identified_by"), collection_E41)
t(collection_E41, RDFS.label, l(collection_row[1].value))
t(collection, crm("P2_has_type"), she_ns("14926d58-83e7-4414-90a8-1a3f5ca8fec1"))
# Creation
collection_E65 = she(cache_40CM.get_uuid(["collection", "E65"], True))
t(collection_E65, a, crm("E65_Creation"))
t(collection_E65, crm("P94_has_created"), collection)
t(collection_E65, crm("P14_carried_out_by"), she(collection_row[2].value))
# Licence
collection_E30 = she(cache_40CM.get_uuid(["collection", "E30"], True))
t(collection_E30, a, crm("E30_Right"))
t(collection, crm("P104_is_subject_to"), collection_E30)
t(collection_E30, RDFS.label, l(collection_row[5].value))
# Attribution
t(collection, crm("P105_right_held_by"), she_ns("48a8e9ad-4264-4b0b-a76d-953bc9a34498"))

#####################################################################
# 1. UNE PUBLICATION NUMERISEE
#####################################################################

if collection_row[3].value == "Edition":

	# Work
	livre_F1 = she(cache_40CM.get_uuid(["collection", "livre", "F1"], True))
	t(livre_F1, a, lrm("F1_Work"))
	livre_E35 = she(cache_40CM.get_uuid(["collection", "livre", "E41"], True))
	t(livre_F1, crm("P102_has_title"), livre_E35)
	t(livre_E35, a, crm("E35_Title"))
	t(livre_E35, RDFS.label, l(collection_row[1].value))

	# Work Conception
	livre_F27 = she(cache_40CM.get_uuid(["collection", "livre", "F27"], True))
	t(livre_F27, a, lrm("F27_Work_Conception"))
	t(livre_F27, lrm("R16_initiated"), livre_F1)
	t(livre_F27, crm("P14_carried_out_by"), l(collection_row[7].value))
	if collection_row[8].value != None:
		livre_F27_E52 = she(cache_40CM.get_uuid(["collection", "livre", "F27_E52"], True))
		t(livre_F27, crm("P4_has_time-span"), livre_F27_E52)
		t(livre_F27_E52, crm("P80_end_is_qualified_by"), l(collection_row[8].value))

	# Expression
	livre_F2 = she(cache_40CM.get_uuid(["collection", "livre", "F2"], True))
	t(livre_F1, lrm("R3_is_realised_in"), livre_F2)
	t(livre_F2, a, lrm("F2_Expression"))
	# Expression Creation
	livre_F28 = she(cache_40CM.get_uuid(["collection", "livre", "F28"], True))
	t(livre_F28, a, lrm("F28_Expression_Creation"))
	t(livre_F28, lrm("R17_created"), livre_F2)
	t(livre_F28, crm("P14_carried_out_by"), l(collection_row[7].value))
	if collection_row[9].value != None:
		livre_F28_E52 = she(cache_40CM.get_uuid(["collection", "livre", "F28_E52"], True))
		t(livre_F28, crm("P4_has_time-span"), livre_F28_E52)
		t(livre_F28_E52, crm("P80_end_is_qualified_by"), l(collection_row[9].value))

	# Manifestation
	livre_F3 = she(cache_40CM.get_uuid(["collection", "livre", "F3"], True))
	t(livre_F3, a, lrm("F3_Manifestation"))
	t(livre_F3, lrm("R4_embodies"), livre_F2)
	## Manifestation Creation
	livre_F30 = she(cache_40CM.get_uuid(["collection", "livre", "F30"], True))
	t(livre_F30, a, lrm("F30_Manifestation_Creation"))
	t(livre_F30, lrm("R24_created"), livre_F3)
	t(livre_F30, crm("P92_brought_into_existence"), livre_F2)
	if collection_row[10].value != None:
		livre_F30_E52 = she(cache_40CM.get_uuid(["collection", "livre", "F30_E52"], True))
		t(livre_F30, crm("P4_has_time-span"), livre_F30_E52)
		t(livre_F30_E52, crm("P80_end_is_qualified_by"), l(collection_row[10].value))
	# Item
	livre_F5 = she(cache_40CM.get_uuid(["collection", "livre", "F5"], True))
	t(livre_F5, a, lrm("F5_Item"))
	t(livre_F5, lrm("R7_is_materialization_of"), livre_F3)

	#####################################################################
	# LES PAGES DE LA PUBLICATION
	#####################################################################

	img_row = None

	for row in img:
		if row[1].value == args.collection_id:
			img_row = row
			id = img_row[0].value

			# La page comme support physique
			page_E18 = she(cache_40CM.get_uuid(["collection", "livre", "pages", id, "E18"], True))
			t(page_E18, a, crm("E18_Physical_Object"))
			t(livre_F5, crm("P46_is_composed_of"), page_E18)

			# La page comme support sémiotique
			page_E90 = she(cache_40CM.get_uuid(["collection", "livre", "pages", id, "E90"], True))
			t(page_E90, a, crm("E90_Symbolic_Object"))
			t(livre_F2, lrm("R15_has_fragment"), page_E90)
			t(page_E18, crm("P128_carries"), page_E90)

			# Identifiant
			page_E42 = she(cache_40CM.get_uuid(["collection", "livre", "pages", id, "E42"], True))
			t(page_E90, crm("P1_is_identified_by"), page_E42)
			t(page_E42, a, crm("E42_Identifier"))
			t(page_E42, RDFS.label, l(id))

			# Numéro de la page
			page_E41 = she(cache_40CM.get_uuid(["collection", "livre", "pages", id, "E42_numéro"], True))
			t(page_E41, crm("P2_has_type"), she_ns("466bb717-b90f-4104-8f4e-5a13fdde3bc3"))
			t(page_E90, crm("P1_is_identified_by"), page_E41)
			t(page_E41, a, crm("E41_Appellation"))
			t(page_E41, RDFS.label, l(f"Page {img_row[3].value}"))

			# Numérisation de la page
			page_D2 = she(cache_40CM.get_uuid(["collection", "livre", "pages", "D2"], True))
			t(page_D2, a, crmdig("D2_Digitization_Process"))
			t(page_D2, crmdig("L1_digitized"), page_E18)
			page_D1 = she(cache_40CM.get_uuid(["collection", "livre", "pages", id, "D1"], True))
			t((page_D1), a, crmdig("D1_Digital_Object"))
			t(page_D2, crmdig("L11_had_output"), page_D1)
			t(page_D1, crm("130_shows_features_of"), page_E90)
			t(collection, crm("P106_is_composed_of"), page_D1)

			# TODO Transcription de la page

#####################################################################
# 2. UNE COLLECTION D'IMAGES INDIVIDUELLES
#####################################################################

if collection_row[3].value == "Images":

	img_row = None

	for row in img:
		if row[1].value == args.collection_id:
			img_row = row
			id = img_row[0].value
			id_livraison = "MG-" + id[0:-4]

			# L'image comme support physique
			img_E22 = she(cache_40CM.get_uuid(["collection", id, "E22"], True))
			t(img_E22, a, crm("E22_Human-Made_Object"))
			## Création de la gravure
			img_E22_E12 = she(cache_40CM.get_uuid(["collection", id, "E22_E12"], True))
			t(img_E22_E12, a, crm("E12_Production"))
			t(img_E22_E12, crm("P108_has_produced"), img_E22)

			# TODO AJOUTER SCULPSIT INVENIT
			### Invenit
			if img_row[12].value != None:
				img_E22_invenit = she(cache_40CM.get_uuid(["collection", id, "E22_E12_invenit"], True))
				t(img_E22_invenit, a, crm("E12_Production"))
				t(img_E22_invenit, crm("P2_has_type"), she_ns("4d57ac14-247f-4b0e-90ca-0397b6051b8b"))
				t(img_E22_E12, crm("P9_consists_of"), img_E22_invenit)
				#### E13 Attribute Assignement

			### Sculpsit
			if img_row[13].value != None:
				img_E22_sculpsit = she(cache_40CM.get_uuid(["collection", id, "E22_E12_sculpsit"], True))
				t(img_E22_sculpsit, a, crm("E12_Production"))
				t(img_E22_sculpsit, crm("P2_has_type"), she_ns("f39eb497-5559-486c-b5ce-6a607f615773"))
				t(img_E22_E12, crm("P9_consists_of"), img_E22_sculpsit)
				#### E13 Attribute Assignement

			# L'image comme support sémiotique
			## E36 Visual Item
			img_E36 = she(cache_40CM.get_uuid(["collection", id, "E36"], True))
			t(img_E22, crm("P65_shows_visual_item"), img_E36)
			t(img_E36, a, crm("E36_Visual_Item"))
			t(img_E36, crm("P1_has_identifier"), l(id))

			## Lien avec la livraison
			try:
				livraison_F2 = she(
					cache_corpus.get_uuid(["Corpus", "Livraisons", id_livraison, "Expression originale", "F2"]))
				t(livraison_F2, crm("P148_has_component"), img_E36)
			except:
				pass

			## TODO AJOUTER LIEN AVEC L'ARTICLE QUAND C'EST POSSIBLE

			## Titre sur l'image (E13)
			if img_row[4].value != None:
				img_E36_titre = she(cache_40CM.get_uuid(["collection", id, "E36_titre_1"], True))
				t(img_E36_titre, a, crm("E13_Attribute_Assignement"))
				t(img_E36_titre, crm("P14_carried_out_by"), she_ns("ea287800-4345-4649-af12-7253aa185f3f"))
				t(img_E36_titre, crm("P140_assigned_attribute_to"), img_E36)
				t(img_E36_titre, crm("P141_assigned"), l(img_row[4].value))
				t(img_E36_titre, crm("P177_assigned_property_type"), she_ns("01a07474-f2b9-4afd-bb05-80842ecfb527"))

			## Titre descriptif/forgé (E13)
			if img_row[5].value != None:
				img_E36_titre = she(cache_40CM.get_uuid(["collection", id, "E36_titre_2"], True))
				t(img_E36_titre, a, crm("E13_Attribute_Assignement"))
				t(img_E36_titre, crm("P14_carried_out_by"), she_ns("ea287800-4345-4649-af12-7253aa185f3f"))
				t(img_E36_titre, crm("P140_assigned_attribute_to"), img_E36)
				t(img_E36_titre, crm("P141_assigned"), l(img_row[5].value))
				t(img_E36_titre, crm("P177_assigned_property_type"), she_ns("58fb99dd-1ffb-4e00-a16f-ef6898902301"))

			## Titre dans le péritexte (E13)
			if img_row[6].value != None:
				img_E36_titre = she(cache_40CM.get_uuid(["collection", id, "E36_titre_3"], True))
				t(img_E36_titre, a, crm("E13_Attribute_Assignement"))
				t(img_E36_titre, crm("P14_carried_out_by"), she_ns("ea287800-4345-4649-af12-7253aa185f3f"))
				t(img_E36_titre, crm("P140_assigned_attribute_to"), img_E36)
				t(img_E36_titre, crm("P141_assigned"), l(img_row[6].value))
				t(img_E36_titre, crm("P177_assigned_property_type"), she_ns("ded9ea93-b400-4550-9aa8-e5aac1d627a0"))

			## Objet ou lieu représenté (E13)
			if img_row[8].value != None:

				# TODO ALIGNER SUR LES E55 QUAND ON AURA TRANSFORME LE VOCABULAIRE D'INDEXATION EN TTL
				# TODO ALIGNER SUR LE REFERENTIEL DES PERSONNES

				### Zone de l'image comportant la représentation de l'objet (E13)
				img_objets = she(cache_40CM.get_uuid(["collection", id, "E36_objets"], True))
				t(img_objets, a, crm("E36_Visual_Item"))
				img_objets_E36_E13 = she(cache_40CM.get_uuid(["collection", id, "E36_objets_E36_E13"], True))
				t(img_objets_E36_E13, a, crm("E13_Attribute_Assignement"))
				t(img_objets_E36_E13, crm("P14_carried_out_by"), she_ns("ea287800-4345-4649-af12-7253aa185f3f"))
				t(img_objets_E36_E13, crm("P140_assigned_attribute_to"), img_E36)
				t(img_objets_E36_E13, crm("P141_assigned"), img_objets)
				t(img_objets_E36_E13, crm("P177_assigned_property_type"), crm("P106_is_composed_of"))

				### L'objet représenté (E13)
				img_objets_E13 = she(cache_40CM.get_uuid(["collection", id, "E36_objets_E13"], True))
				t(img_objets_E13, a, crm("E13_Attribute_Assignement"))
				t(img_objets_E13, crm("P14_carried_out_by"), she_ns("ea287800-4345-4649-af12-7253aa185f3f"))
				t(img_objets_E13, crm("P140_assigned_attribute_to"), img_objets)
				t(img_objets_E13, crm("P141_assigned"), l(img_row[8].value))
				t(img_objets_E13, crm("P177_assigned_property_type"), crm("P138_represents"))

				### Si l'objet représenté est une médaille (E13)
				if "médaille" in img_row[8].value:
					img_médaille = she(cache_40CM.get_uuid(["collection", id, "E36_médaille"], True))
					t(img_médaille, a, crm("E36_Visual_Item"))
					t(img_médaille, crm("P2_has_type"), she_ns("4b51d9dc-3623-47f4-ab45-239604e18930"))
					t(img_médaille, RDFS.label, l("Médaille"))
					#### E13 Attribute Assignement
					img_médaille_E13 = she(cache_40CM.get_uuid(["collection", id, "E36_médaille_E13"], True))
					t(img_médaille_E13, a, crm("E13_Attribute_Assignement"))
					t(img_médaille_E13, crm("P14_carried_out_by"), she_ns("ea287800-4345-4649-af12-7253aa185f3f"))
					t(img_médaille_E13, crm("P140_assigned_attribute_to"), img_E36)
					t(img_médaille_E13, crm("P141_assigned"), img_médaille)
					t(img_médaille_E13, crm("P177_assigned_property_type"), crm("P106_is_composed_of"))

					#### Si la médaille comporte une inscription
					img_médaille_inscrip_E36 = she(
						cache_40CM.get_uuid(["collection", id, "E36_médaille_inscrip_E36"], True))
					t(img_médaille_inscrip_E36, a, crm("E36_Visual_Item"))
					t(img_médaille_inscrip_E36, RDFS.label, l("Zone d'inscription"))
					##### E13 Attribute Assignement
					img_médaille_inscrip_E13 = she(
						cache_40CM.get_uuid(["collection", id, "E36_médaille_E36_E13"], True))
					t(img_médaille_inscrip_E13, a, crm("E13_Attribute_Assignement"))
					t(img_médaille_inscrip_E13, crm("P14_carried_out_by"), she_ns("ea287800-4345-4649-af12-7253aa185f3f"))
					t(img_médaille_inscrip_E13, crm("P140_assigned_attribute_to"), img_médaille)
					t(img_médaille_inscrip_E13, crm("P141_assigned"), img_médaille_inscrip_E36)
					t(img_médaille_inscrip_E13, crm("P177_assigned_property_type"), crm("P106_is_composed_of"))

					##### Si la médaille comporte une inscription en légende (E13)
					if img_row[14].value != None:
						img_médaille_inscrip_E33 = she(
							cache_40CM.get_uuid(["collection", id, "E36_médaille_E33_leg"], True))
						t(img_médaille_inscrip_E33, a, crm("E33_Linguistic_Object"))

						##### E13 Attribute Assignement du E33
						img_médaille_inscrip_E33_E13 = she(
							cache_40CM.get_uuid(["collection", id, "E36_médaille_E33_E13_leg"], True))
						t(img_médaille_inscrip_E33_E13, a, crm("E13_Attribute_Assignement"))
						t(img_médaille_inscrip_E33_E13, crm("P14_carried_out_by"),
						  she_ns("ea287800-4345-4649-af12-7253aa185f3f"))
						t(img_médaille_inscrip_E33_E13, crm("P140_assigned_attribute_to"), img_médaille_inscrip_E36)
						t(img_médaille_inscrip_E33_E13, crm("P141_assigned"), img_médaille_inscrip_E33)
						t(img_médaille_inscrip_E33_E13, crm("P177_assigned_property_type"), crm("P165_incorporates"))
						t(img_médaille_inscrip_E33_E13, she_ns("sheP_position_du_texte_par_rapport_à_la_médaille"),
						  she_ns("fc229531-0999-4499-ab0b-b45e18e8196f"))

						##### E13 Attribute Assignement du contenu de l'inscription
						img_médaille_inscrip_P190_E13 = she(
							cache_40CM.get_uuid(["collection", id, "E36_médaille_E33_leg_P190"], True))
						t(img_médaille_inscrip_P190_E13, a, crm("E13_Attribute_Assignement"))
						t(img_médaille_inscrip_P190_E13, crm("P14_carried_out_by"),
						  she_ns("ea287800-4345-4649-af12-7253aa185f3f"))
						t(img_médaille_inscrip_P190_E13, crm("P140_assigned_attribute_to"), img_médaille_inscrip_E33)
						t(img_médaille_inscrip_P190_E13, crm("P141_assigned"), l(img_row[14].value))
						t(img_médaille_inscrip_P190_E13, crm("P177_assigned_property_type"), crm("P190_has_symbolic_content"))

					##### Si la médaille comporte une inscription en exergue (E13)
					if img_row[15].value != None:
						img_médaille_inscrip_E33 = she(
							cache_40CM.get_uuid(["collection", id, "E36_médaille_E33_ex"], True))
						t(img_médaille_inscrip_E33, a, crm("E33_Linguistic_Object"))

						##### E13 Attribute Assignement du E33
						img_médaille_inscrip_E33_E13 = she(
							cache_40CM.get_uuid(["collection", id, "E36_médaille_E33_E13_ex"], True))
						t(img_médaille_inscrip_E33_E13, a, crm("E13_Attribute_Assignement"))
						t(img_médaille_inscrip_E33_E13, crm("P14_carried_out_by"),
						  she_ns("ea287800-4345-4649-af12-7253aa185f3f"))
						t(img_médaille_inscrip_E33_E13, crm("P140_assigned_attribute_to"), img_médaille_inscrip_E36)
						t(img_médaille_inscrip_E33_E13, crm("P141_assigned"), img_médaille_inscrip_E33)
						t(img_médaille_inscrip_E33_E13, crm("P177_assigned_property_type"), crm("P165_incorporates"))
						t(img_médaille_inscrip_E33_E13, she_ns("sheP_position_du_texte_par_rapport_à_la_médaille"),
						  she_ns("357a459f-4f27-4d46-b5ac-709a410bce04"))

						##### E13 Attribute Assignement du contenu de l'inscription
						img_médaille_inscrip_P190_E13 = she(
							cache_40CM.get_uuid(["collection", id, "E36_médaille_E33_ex_P190"], True))
						t(img_médaille_inscrip_P190_E13, a, crm("E13_Attribute_Assignement"))
						t(img_médaille_inscrip_P190_E13, crm("P14_carried_out_by"),
						  she_ns("ea287800-4345-4649-af12-7253aa185f3f"))
						t(img_médaille_inscrip_P190_E13, crm("P140_assigned_attribute_to"), img_médaille_inscrip_E33)
						t(img_médaille_inscrip_P190_E13, crm("P141_assigned"), l(img_row[15].value))
						t(img_médaille_inscrip_P190_E13, crm("P177_assigned_property_type"),
						  crm("P190_has_symbolic_content"))

serialization = output_graph.serialize(format="turtle", base="http://data-iremus.huma-num.fr/id/")
with open(args.output_ttl, "wb") as f:
	f.write(serialization)
cache_40CM.bye()
cache_corpus.bye()
