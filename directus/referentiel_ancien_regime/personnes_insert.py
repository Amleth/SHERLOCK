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

parser = argparse.ArgumentParser()
parser.add_argument("--cache_personnes")
parser.add_argument("--cache_corpus")
parser.add_argument("--skos")
args = parser.parse_args()

# SECRET YAML
file = open(os.path.join(sys.path[0], "secret.yaml"))
secret = yaml.full_load(file)
r = requests.post(secret["url"] + "/auth/login", json={"email": secret["email"], "password": secret["password"]})
access_token = r.json()['data']['access_token']
refresh_token = r.json()['data']['refresh_token']
file.close()

# DONNEES DE LA BASE
r = requests.get(secret["url"] + '/items/sources_articles/MG-1678-01_206?access_token=' + access_token)
# pprint(r.json())
r = requests.get(secret["url"] + '/items/sources_articles_indices/1?access_token=' + access_token)
# pprint(r.json())
r = requests.get(secret["url"] + '/items/sources_articles_indices/2?access_token=' + access_token)
# pprint(r.json())

# CACHE
cache_corpus = Cache(args.cache_corpus)
cache_personnes = Cache(args.cache_personnes)

# GRAPHE
input_graph = Graph()
input_graph.load(args.skos)

# RECUPERATION DES DONNEES
dict_indexations = {}

for opentheso_personne_uri, p, o in input_graph.triples((None, RDF.type, SKOS.Concept)):

	infos = {}

	id = list(input_graph.objects(opentheso_personne_uri, DCTERMS.identifier))[0].value
	uuid = cache_personnes.get_uuid(["personnes", id, "uuid"])
	infos["id"] = uuid
	label = list(input_graph.objects(opentheso_personne_uri, SKOS.prefLabel))[0].value
	infos["label"] = label
	definitions = list(input_graph.objects(opentheso_personne_uri, SKOS.definition))
	if len(definitions) >= 1:
		infos["definition"] = definitions[0]

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
					indexation = indexation.replace("##", "").strip()
					dict_indexations[indexation] = []
					dict_indexations[indexation].append(uuid)
			else:
				notes.append(note.value)

	if len(notes) == 1:
		infos["note_1"] = notes[0]
	elif len(notes) >= 1:
		infos["note_2"] = notes[1]

# INSERTION DES DONNEES

r = requests.patch(secret["url"] + '/items/personnes?access_token=' + access_token, json=infos)
# print(dict_indexations)

# # Boucler sur tous les concepts skos et les créer avec leurs champs non-relationnels
# # Maintenir un dictionnaire des indexations dont les clés seraient les codes des articles et les valeurs un tableau des uuid des personnes.
# # Une fois la boucle sur les concepts terminée, on itère sur le dictionnaire des indexations et on crée un article par clé et le tableau des indexations dans son champ indices
# # Toujours vérifier si l'article existe dans le dictionnaire des indexations
#
#
#
# # from pprint import pprint
# #
# # dic = {
# #     'MG-X-Y-Z': [
# #         'b47b2d56-c080-4455-9126-9bd06bc50276',
# #         'd7687d5e-aae7-48c7-ba9c-7104253cf80b'
# #     ],
# #     'MG-A-B-C': [
# #         '3de043d0-7b70-4ad1-a644-d1243c308a69',
# #         'd7687d5e-aae7-48c7-ba9c-7104253cf80b',
# #         'b92f3546-b03d-4ff3-a314-d6683a6fd1c8'
# #     ]
# # }
# #
# # for k, v in dic.items():
# #     json = {
# #         "id": k,
# #         "indices": [{
# #             "item": i,
# #             "sources_articles_id": k,
# #             "collection": "personnes"
# #         } for i in v]
# #     }
# #     pprint(json)


# r = requests.post(
# 	secret["url"] + '/items/sources_articles?access_token=' + access_token,
# 	json={
# 		'id': "MG-1678-01_206",
# 		'indices': [
# 			{
# 				"item": "850c7a5d-71b3-4e46-98a2-c2773bc5bf79",
# 				"sources_articles_id": "MG-1678-01_206",
# 				"collection": "personnes"
# 			}]
# 	}
# )