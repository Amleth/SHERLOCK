import argparse
from rdflib import Graph, Literal, Namespace, DCTERMS, RDF, RDFS, SKOS, URIRef, URIRef as u, Literal as l
import re

################################################################################
### Ouverture du graphe et du fichier texte
################################################################################

parser = argparse.ArgumentParser()
parser.add_argument("--inputrdf")
parser.add_argument("--outputtxt")
args = parser.parse_args()

input_graph = Graph()
input_graph.load(args.inputrdf)

output_txt = open(args.outputtxt, "w")

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
	municipalites = ro_list(opentheso_municipalite_uri, SKOS.narrower)
	for municipalite in municipalites:
		institutions = ro_list(municipalite, SKOS.narrower)
		for institution in institutions:
			entrees = (ro_list(institution, SKOS.prefLabel))

			lst = []
			for entree in entrees:
				if "Corps de ville" in entree:
					lst.append("Corps de ville")
					pass

				else:
					e = re.search(".*(?=de)", entree)
					print(e)

			#print(lst)