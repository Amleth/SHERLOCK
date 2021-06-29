import json
import subprocess
from subprocess import call
from rdflib import Graph, Literal, RDF, RDFS, SKOS, DCTERMS
from rdflib.plugins import sparql
import argparse
from sherlockcachemanagement import Cache
import yaml
import os
import sys
import requests
from pprint import pprint

# Arguments
parser = argparse.ArgumentParser()
parser.add_argument("--cache_personnes")
parser.add_argument("--cache_corpus")
parser.add_argument("--skos")
args = parser.parse_args()

# Secret YAML
file = open(os.path.join(sys.path[0], "secret.yaml"))
secret = yaml.full_load(file)
r = requests.post(secret["url"] + "/auth/login", json={"email": secret["email"], "password": secret["password"]})
access_token = r.json()['data']['access_token']
refresh_token = r.json()['data']['refresh_token']
file.close()

# Test - lecture de données
# r = requests.get(secret["url"] + '/items/sources_articles/MG-1678-01_206?access_token=' + access_token)
# pprint(r.json())
# r = requests.get(secret["url"] + '/items/sources_articles_indices/1?access_token=' + access_token)
# pprint(r.json())
# r = requests.get(secret["url"] + '/items/sources_articles_indices/2?access_token=' + access_token)
# pprint(r.json())

# Caches
cache_corpus = Cache(args.cache_corpus)
cache_personnes = Cache(args.cache_personnes)

# Initialisation du graphe
input_graph = Graph()
input_graph.load(args.skos)

# Dictionnaire des concepts et de leurs informations
dict_infos_concept = {}

# Dictionnaire de l'indexation des sources par le référentiel des personnes
dict_indexations = {}


#########################################################################################
## INSERTION DES PERSONNES ET LEURS INFORMATIONS DANS DIRECTUS
#########################################################################################

# RECUPERATION DES DONNEES
for opentheso_personne_uri, p, o in input_graph.triples((None, RDF.type, SKOS.Concept)):

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
			note = notes_opentheso[0]
			if "##id##" in note or note.startswith("##"):
				indexations = note.split("##id##")
				for indexation in indexations:
					if indexation == None:
						continue
					indexation = indexation.replace("##", "").strip().split(" ")
					indexation = indexation[0]

					# TODO Corriger les erreurs d'encodage dans l'indexation
					if "&" in indexation or "<" in indexation or indexation == None:
						#print(note)
						pass

					if indexation not in dict_indexations:
						dict_indexations[indexation] = []
					dict_indexations[indexation].append(uuid)
			else:
				notes.append(note.value)

	if len(notes) >= 1:
		dict_infos_concept["note_1"] = notes[0]
		if len(notes) >= 2:
			dict_infos_concept["note_2"] = notes[1]
		else:
			dict_infos_concept["note_2"] = None
	else:
		dict_infos_concept["note_1"] = None
		dict_infos_concept["note_2"] = None

	# ENVOI DES DONNEES
	# r = requests.post(secret["url"] + '/items/personnes?access_token=' + access_token, json=dict_infos_concept)

	# RECUPERATION DES ALTLABELS
	altlabels = list(input_graph.objects(opentheso_personne_uri, SKOS.altLabel))
	if altlabels != None:
		for altlabel in altlabels:
			dict_altlabels_concept = {
				"id": uuid,
				"personnes_altlabels": [{
					"label": altlabel.value,
					"personne": uuid
				}]
			}

			# pprint(dict_altlabels_concept)

			# ENVOI DES DONNEES
			# r = requests.patch(secret["url"] + '/items/personnes?access_token=' + access_token, json=dict_altlabels_concept)
	else:
		pass

#########################################################################################
## INSERTION DES INDEXATION DES SOURCES DANS DIRECTUS
#########################################################################################

for k, v in dict_indexations.items():
	dict_infos_index = {
		"id": k,
		"indices": [{
			"item": i,
			"sources_articles_id": k,
			"collection": "personnes"
		} for i in v]
	}

	# pprint(dict_infos_index)

	# ENVOI DES DONNEES
	# r = requests.post(secret["url"] + '/items/sources_articles?access_token=' + access_token, json=dict_infos_index)


