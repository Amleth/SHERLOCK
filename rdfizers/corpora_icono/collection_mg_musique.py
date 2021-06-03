import argparse
from rdflib import Literal as l, RDF, RDFS, URIRef as u
from helpers_python import get_xlsx_rows_as_dicts
from helpers_rdf import a, crm, crmdig, init_graph, save_graph, she, t
from sherlockcachemanagement import Cache
import glob
import ntpath

parser = argparse.ArgumentParser()
parser.add_argument("--ttl")
parser.add_argument("--xlsx")
parser.add_argument("--cache")
parser.add_argument("--cache_corpus")
parser.add_argument("--dossier_coll")
args = parser.parse_args()

cache = Cache(args.cache)
if args.cache_corpus:
    cache_corpus = Cache(args.cache_corpus)

init_graph()

for img in glob.glob(args.dossier_coll + '/*.JPG', recursive=False):

	id = ntpath.basename(img[:-4])

	collection = she("3a0fcd6a-c226-49f4-ac11-5eff8448ee55")

	# E36 Visual Item
	gravure = she(cache.get_uuid(["collection", id, "gravure (E36)", "uuid"], True))
	t(gravure, a, crm("E36_Visual_Item"))
	t(collection, crm("P148_has_component"), gravure)

	# Identifiant Mercure Galant
	gravure_id_MG = she(cache.get_uuid(["collection", id, "gravure (E36)", "Identifiant MG"], True))
	t(gravure_id_MG, a, crm("E42_Identifier"))
	t(gravure_id_MG, crm("P2_has_type"), she("92c258a0-1e34-437f-9686-e24322b95305"))
	t(gravure_id_MG, RDFS.label, l(id))
	t(gravure, crm("P1_is_identified_by"), gravure_id_MG)

	# Identifiant IIIF
	gravure_id_iiif = she(cache.get_uuid(["collection", id, "gravure (E36)", "Identifiant iiif"], True))
	t(gravure_id_iiif, a, crm("E42_Identifier"))
	t(gravure_id_iiif, crm("P2_has_type"), she("19073c4a-0ef7-4ac4-a51a-e0810a596773"))
	t(gravure_id_iiif, RDFS.label,
	  u(f"http://data-iremus.huma-num.fr/iiif/3/mg_musique--{id.replace(' ', '%20')}/full/max/0/default.jpg"))
	t(gravure, crm("P1_is_identified_by"), gravure_id_iiif)

	# Identifiant GitHub
	gravure_id_github = she(
		cache.get_uuid(["collection", id, "gravure (E36)", "Identifiant GitHub"], True))
	t(gravure_id_github, a, crm("E42_Identifier"))
	t(gravure_id_github, crm("P2_has_type"), she("cdbec0af-a5c4-49e2-8a71-4a6fc43dd3ea"))
	t(gravure_id_github, RDFS.label,
	  u(
		  f"https://github.com/OBVIL/mercure-galant/blob/0ba4cfdbb66ccf7ed6af0a92bf1490a998e95b3c/images/{id.replace(' ', '%20')}.JPG"))
	t(gravure, crm("P1_is_identified_by"), gravure_id_github)

	# Rattachement à l'article
	try:

		if "copyOf" in id:
			parties_de_l_id = id.split(" ")

			id_article = parties_de_l_id[0]
			# TODO Ajouter xyz au nom des gravures en plusieurs parties plutôt que abc
			if id_article.endswith("x") or id_article.endswith("y") or id_article.endswith("z"):
				id_article = id_article[:-1]

			id_livraison = id_article[:-4]
			if id_livraison.endswith("_"):
				id_livraison = id_livraison[:-1]

			article_F2 = she(cache_corpus.get_uuid(
				["Corpus", "Livraisons", id_livraison, "Expression originale", "Articles", id_article, "F2"]))
			t(article_F2, crm("P148_has_component"), gravure)

		else:

			id_article = id
			# TODO Ajouter xyz au nom des gravures en plusieurs parties plutôt que abc
			if id_article.endswith("x") or id_article.endswith("y") or id_article.endswith("z"):
				id_article = id_article[:-1]

			id_livraison = id_article[:-4]
			if id_livraison.endswith("_"):
				id_livraison = id_livraison[:-1]

			article_F2 = she(cache_corpus.get_uuid(
				["Corpus", "Livraisons", id_livraison, "Expression originale", "Articles", id_article, "F2"]))
			t(article_F2, crm("P148_has_component"), gravure)
	except:
		print("Impossible de retrouver l'article de la gravure", id_article, "(livraison " + id_livraison + ")")

###################################################################################################
# Création du graphe et du cache
###################################################################################################

cache.bye()
save_graph(args.ttl)