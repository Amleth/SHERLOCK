import json
import subprocess
from subprocess import call
from rdflib import Graph, Literal
from rdflib.plugins import sparql
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--ttl")
args = parser.parse_args()

#####################################################################################
## FUNCTIONS
#####################################################################################

# def system_call(command):
#     p = subprocess.Popen([command], stdout=subprocess.PIPE, shell=True)
#     tmp = str(p.stdout.read()).replace('\\n', ' ')
#     return tmp[2: len(tmp) - 1]
#
# def token_generation(email, pwd, url):
#     auth_json = '{ "email" : "%s", "password" : "%s"}' % (email, pwd)
#     token_request = system_call(
#         "curl -X POST -H 'Content-Type: application/json' --data '%s' %s/auth/login" % (auth_json, url))
#     return str(json.loads(token_request)['data']['access_token'])

def recuperation_donnees():

	input_graph = Graph()
	input_graph.load(args.ttl, format="turtle")

	q = sparql.prepareQuery("""
		PREFIX crm: <http://www.cidoc-crm.org/cidoc-crm/>
		PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
		SELECT ?prefLabel
		WHERE {
		?concept crm:P1_is_identified_by ?E41 .
		?E41 a crm:E41_Appellation .
		?E41 rdfs:label ?prefLabel .
		}""")

	for row in input_graph.query(q):
		label = row[0]
		print(label)

recuperation_donnees()


#####################################################################################
## MAIN
#####################################################################################

# email = 'thomas.bottini@cnrs.fr'
# pwd = '14a32e3e-bc5a-4c7d-83f6-6aea62baaab2'
# url = 'http://bases-iremus.huma-num.fr/directus-rar/'
#
# token = token_generation(email, pwd, url)
# print("________________________")
# print("|                      |")
# print("|      Insertion       |")
# print("|     des données      |")
# print("|                      |")
# print("‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾")
# print("Connexion à l'API de Directus | Token : " + token)

# ttl_path = 'personnes.ttl'
# sheet_names = ['airs',
#                'éditions',
#                'textes_publiés',
#                'références_externes',
#                'thèmes',
#                'timbres',
#                'assoc_air_référence',
#                'assoc_texte_thème',
#                'assoc_texte_référence',
#                'assoc_référence_édition'
#                ]
#
# mon_cache = Cache("fichier-cache.yaml")