import argparse
from rdflib import Graph, Literal, Namespace, DCTERMS, RDF, RDFS, SKOS, URIRef, URIRef as u, Literal as l
import re
import json

################################################################################
### Ouverture du graphe et du fichier texte
################################################################################

parser = argparse.ArgumentParser()
parser.add_argument("--inputrdf")
parser.add_argument("--outputtxt")
args = parser.parse_args()

input_graph = Graph()
input_graph.load(args.inputrdf)

outputtxt = open(args.outputtxt, "w")

################################################################################
### Fonctions
################################################################################

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

################################################################################
### Récupération des données
################################################################################

for opentheso_municipalite_uri, p, o in input_graph.triples((URIRef("http://opentheso3.mom.fr/opentheso3/?idc=municipalite&idt=173"), RDF.type, SKOS.Concept)):

	# On récupère l'URI de la municipalité
	municipalites_uri = ro_list(opentheso_municipalite_uri, SKOS.narrower)

	lst = {}

	# On récupère les URIs des institutions/fonctions de chaque municipalité
	for municipalite in municipalites_uri:
		institutions_uri = ro_list(municipalite, SKOS.narrower)

		# On récupère leur nom
		for institution in institutions_uri:
			institution_prefLabel = (ro_list(institution, SKOS.prefLabel))

			# On transforme chaque valeur en clé de dictionnaire
			for chaine_caract in institution_prefLabel:

				# On crée la clé "Corps de ville"
				cle = "Corps de ville"
				lst.setdefault(cle, [])

				if "Corps de ville" in chaine_caract:
					# On ajoute les valeurs de chaque clé en supprimant le nom de la municipalité
					narrower = (ro(institution, SKOS.narrower))
					if narrower != None:
						narrower_prefLabel = str((ro(narrower, SKOS.prefLabel)))
						n = re.search(".*(?= de| d\'A)", narrower_prefLabel)
						if n != None:
							n_group = n.group()
							if n_group not in lst[cle]:
								lst[cle].append(n_group)
								pass

				# On ajoute les autres clés en supprimant le nom de la municipalité
				else:
					e = re.search(".*(?= de | d\'A)", chaine_caract)
					if e != None:
						e_group = e.group()
						if e_group not in lst:
							lst.setdefault(e_group, [])

							# On ajoute leurs valeurs en supprimant le nom de la municipalité
						narrower = (ro(institution, SKOS.narrower))
						if narrower != None:
							narrower_prefLabel = str((ro(narrower, SKOS.prefLabel)))
							if n != None:
								n = re.search(".*(?= de | d\'A|)", narrower_prefLabel)
								n_group = n.group()
								if n_group not in lst[e_group]:
									lst[e_group].append(n_group)


test = json.dumps(lst, indent = 4, ensure_ascii=False)
outputtxt.write(test)
print(test)

