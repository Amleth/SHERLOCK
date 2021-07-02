import json
import subprocess
from subprocess import call
from rdflib import Graph, Literal, RDF, RDFS, SKOS, DCTERMS
from rdflib.plugins import sparql
import argparse
from sherlockcachemanagement import Cache
from pprint import pprint
import time

# Arguments
parser = argparse.ArgumentParser()
parser.add_argument("--cache_personnes")
parser.add_argument("--cache_corpus")
parser.add_argument("--skos")
parser.add_argument("--json_concepts")
parser.add_argument("--json_index")
args = parser.parse_args()

# Caches
cache_corpus = Cache(args.cache_corpus)
cache_personnes = Cache(args.cache_personnes)

# Initialisation du graphe
input_graph = Graph()
input_graph.load(args.skos)

# Dictionnaire de l'indexation des sources par le référentiel des personnes
dict_indexations = {}

#########################################################################################
## PERSONNES
#########################################################################################

data_concepts = []

# RECUPERATION DES DONNEES
for opentheso_personne_uri, p, o in input_graph.triples((None, RDF.type, SKOS.Concept)):

	# Dictionnaire des concepts et de leurs informations
	dict_infos_concept = {}

	id = list(input_graph.objects(opentheso_personne_uri, DCTERMS.identifier))[0].value

	# uuid
	uuid = cache_personnes.get_uuid(["personnes", id, "uuid"])
	dict_infos_concept["id"] = uuid

	# prefLabel
	label = list(input_graph.objects(opentheso_personne_uri, SKOS.prefLabel))[0].value
	dict_infos_concept["label"] = label

	# définition
	definitions = list(input_graph.objects(opentheso_personne_uri, SKOS.definition))
	if len(definitions) >= 1:
		dict_infos_concept["definition"] = definitions[0].value
	else:
		dict_infos_concept["definition"] = None

	# notes/indexation
	notes = []
	for p in [SKOS.editorialNote, SKOS.historyNote, SKOS.note, SKOS.scopeNote]:
		notes_opentheso = list(input_graph.objects(opentheso_personne_uri, p))
		if len(notes_opentheso) >= 1:
			note = notes_opentheso[0].value

			# balises dans les notes à supprimer
			balises_a_supprimer = ["&amp;nbsp;", "<p class= ql-align-justify >", "<br>",
			"</span>", "</p>", "<span style= color: black; >", "<span style= color: rgb(102, 102, 102); >",
			"<span style= color: rgb(0, 0, 0); >", "<span style= color: rgb(80, 80, 80); >",
			"<span style= color: rgb(191, 191, 191); >", "<p>"]
			for balise in balises_a_supprimer:
				if balise in note:
					note = note.replace(balise, "")

			# récupération des indexations
			if "##" in note:
				indexations = note.split("##")
				for indexation in indexations:
					if "MG" in indexation:
						indexation = indexation.replace("\r", "").strip()

						if indexation not in dict_indexations:
							dict_indexations[indexation] = []
						dict_indexations[indexation].append(uuid)

			else:
				notes.append(note)

	if len(notes) >= 1:
		dict_infos_concept["note_1"] = notes[0]
		if len(notes) >= 2:
			dict_infos_concept["note_2"] = notes[1]
		else:
			dict_infos_concept["note_2"] = None
	else:
		dict_infos_concept["note_1"] = None
		dict_infos_concept["note_2"] = None

	# RECUPERATION DES ALTLABELS
	altlabels = list(input_graph.objects(opentheso_personne_uri, SKOS.altLabel))
	if altlabels != None:
		dict_infos_concept["personnes_altlabels"] = [
			{
				"label": altlabel.value,
				"personne": uuid
			}
			for altlabel in altlabels]

	# time.sleep(0.5)

	data_concepts.append(dict_infos_concept)

#########################################################################################
## INDEXATIONS
#########################################################################################

data_index = []

for k, v in dict_indexations.items():
	dict_infos_index = {
		"id": k,
		"indices": [{
			"item": i,
			"sources_articles_id": k,
			"collection": "personnes"
		} for i in v]
	}

	data_index.append(dict_infos_index)

#########################################################################################
## CREATION DES FICHIERS JSON
#########################################################################################

with open(args.json_concepts, 'w', encoding="utf-8") as file:
	json.dump(data_concepts, file, ensure_ascii=False)

with open(args.json_index, 'w', encoding="utf-8") as file:
	json.dump(data_index, file, ensure_ascii=False)
