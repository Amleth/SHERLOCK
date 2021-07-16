import json
from rdflib import Graph, Literal, Namespace, DCTERMS, RDF, RDFS, SKOS, URIRef, URIRef as u, Literal as l
import argparse
from pprint import pprint
from sherlockcachemanagement import Cache

# Arguments
parser = argparse.ArgumentParser()
parser.add_argument("--json")
parser.add_argument("--ttl")
parser.add_argument("--cache")
parser.add_argument("--cache_corpus")
args = parser.parse_args()

# Cache
cache = Cache(args.cache)
cache_corpus = Cache(args.cache_corpus)

############################################################################################
## INITIALISATION DU GRAPHE ET NAMESPACES
############################################################################################

output_graph = Graph()

crm_ns = Namespace("http://www.cidoc-crm.org/cidoc-crm/")
iremus_ns = Namespace("http://data-iremus.huma-num.fr/id/")
sdt_ns = Namespace("http://data-iremus.huma-num.fr/datatypes/")
sherlock_ns = Namespace("http://data-iremus.huma-num.fr/ns/sherlock#")

output_graph.bind("crm", crm_ns)
output_graph.bind("dcterms", DCTERMS)
output_graph.bind("skos", SKOS)
output_graph.bind("sdt", sdt_ns)
output_graph.bind("she_ns", sherlock_ns)

a = RDF.type


def crm(x):
	return URIRef(crm_ns[x])


def she(x):
	return URIRef(iremus_ns[x])


def she_ns(x):
	return URIRef(sherlock_ns[x])


def t(s, p, o):
	output_graph.add((s, p, o))


############################################################################################
## RECUPERATION DES DONNEES
############################################################################################

with open(args.json) as f:
	json_file = json.load(f)

	# Indexations
	for indexation in json_file["data"]["sources_articles"]:

		# Identifiant de l'article et de la livraison indexées
		id_livraison = indexation["id"][3:].split("_")
		id_livraison = id_livraison[0]
		id_article = indexation["id"][3:]

		# Récupération de l'uuid de l'article dans le cache du corpus
		try:
			F2_article_uri = she(cache_corpus.get_uuid(
				["Corpus", "Livraisons", id_livraison, "Expression TEI", "Articles", id_article, "F2"]))
		except:
			print("l'article ou la livraison", id_article, "(" + id_livraison + ") est introuvable dans les sources TEI")

		# Insertion des données dans le graphe
		for article in indexation["indices"]:
			try:
				uuid_personne = article["item"]["id"]
				E13_indexation_uri = she(cache.get_uuid(["indexations", id_article, "personnes", uuid_personne, "E13_Attribute_Assignement"], True))
				t(E13_indexation_uri, a, crm("E13_Attribute_Assignement"))
				t(E13_indexation_uri, crm("P14_carried_out_by"),
				  she("684b4c1a-be76-474c-810e-0f5984b47921"))
				t(E13_indexation_uri, crm("P140_assigned_attribute_to"), F2_article_uri)
				t(E13_indexation_uri, crm("P141_assigned"), she(uuid_personne))
				t(E13_indexation_uri, crm("P177_assigned_property_type"), crm("P67_refers_to"))

			except:
				continue

############################################################################################
## SERIALISATION DU GRAPHE
############################################################################################

serialization = output_graph.serialize(format="turtle", base="http://data-iremus.huma-num.fr/id/")
with open(args.ttl, "wb") as f:
	f.write(serialization)

cache.bye()
