from rdflib import Graph
from rdflib.plugins import sparql

############################################################################################
# RECHERCHE DES CONGREGATIONS DONT L'ALIGNEMENT AU REFERENTIEL DES LIEUX N'A PAS FONCTIONNE
############################################################################################

output_graph = Graph()
output_graph.load("./out/referentiel_ancien_regime/referentiel_congregations.ttl")

with open("./sources/referentiel_ancien_regime/congregations_sheP_situation_géohistorique.txt") as txt:
	texte = txt.read()
	for concept_id in texte:
		print(concept_id)


		"""
		q = sparql.prepareQuery("""
		# SELECT ?concept ?lieu
		# WHERE {
		#   ?concept <http://data-iremus.huma-num.fr/ns/sherlock#sheP_situation_géohistorique> ?lieu .
		# }
		""")

		for row in input_graph.query(q, initBindings={'concept': concept_id}):
			print(row[0])

		"""