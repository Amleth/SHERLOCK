from rdflib import Graph, Literal
from rdflib.plugins import sparql
import re

############################################################################################
# RECHERCHE DES CONGREGATIONS DONT L'ALIGNEMENT AU REFERENTIEL DES LIEUX N'A PAS FONCTIONNE
############################################################################################

output_graph = Graph()
output_graph.load("./out/referentiel_ancien_regime/referentiel_congregations.ttl", format="turtle")

file = open("./sources/referentiel_ancien_regime/congregations_sheP_situation_géohistorique.txt", "r", encoding="utf-8")

list = file.readlines()
for id in list:
	concept_id = Literal(id.rstrip())

	q = sparql.prepareQuery("""
		SELECT ?concept_id
		WHERE {
		?concept <http://www.cidoc-crm.org/cidoc-crm/P1_is_identified_by> ?identifier .
		?identifier <http://www.w3.org/2000/01/rdf-schema#label> ?concept_id .
		FILTER NOT EXISTS {
		?concept <http://data-iremus.huma-num.fr/id/sheP_situation_géohistorique> ?lieu .
		}
		}
		""")

	for row in output_graph.query(q, initBindings={'concept_id': concept_id}):
		print(row[0])


	# lieux = ["vienne [Viennois]", "toul", "toulouse", "ris", "paris"]
	# congregations = ["evque de vienne", "truc de toul", "truc de toulouse", "truc à ris", "bidule au truc de Paris"]
	# for lieu in lieux:
	# 	for congreg in congregations:
	# 		if re.search(rf"('| de | la | le | a | du )({lieu} )|( {lieu}$)", congreg, re.IGNORECASE):
	# 			print(lieu, "  -  ", congreg)

