import argparse
from rdflib import Graph, Literal, Namespace, DCTERMS, RDF, RDFS, SKOS, URIRef, URIRef as u, Literal as l
import re
import json
import unidecode

################################################################################
### Ouverture du graphe et du fichier texte
################################################################################

parser = argparse.ArgumentParser()
parser.add_argument("--inputrdf")
parser.add_argument("--outputtxt")
parser.add_argument("--inputttl")
args = parser.parse_args()

input_graph = Graph()
input_graph.load(args.inputrdf)

input_graph_ttl = Graph()
input_graph_ttl.load(args.inputttl, format="turtle")

outputtxt = open(args.outputtxt, "w")

################################################################################
### Fonctions
################################################################################

a = RDF.type

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
### Institutions et fonctions de la branche "municipalités"
################################################################################

# On récupère l'URI de la municipalité
municipalites_uri = ro_list(URIRef("http://opentheso3.mom.fr/opentheso3/?idc=municipalite&idt=173"), SKOS.narrower)

lst = {}

# On récupère les URIs des institutions de chaque municipalité
for municipalite in municipalites_uri:
	institutions_uri = ro_list(municipalite, SKOS.narrower)

	# On récupère le nom des institutions
	for institution in institutions_uri:
		institution_prefLabel = (ro_list(institution, SKOS.prefLabel))

		# On transforme chaque institution en clé de dictionnaire en supprimant le nom de la municipalité
		for chaine_caract in institution_prefLabel:
			cle = re.search("Corps de ville|.*(?= de | d\'A)", chaine_caract)
			if cle != None:
				# On normalise les caractères
				cle_group = cle.group().capitalize()
				cle_group_decode = unidecode.unidecode(cle_group)
				if cle_group_decode not in lst:
					lst.setdefault(cle_group_decode, [])

				# On ajoute leurs valeurs en supprimant le nom de la municipalité
				narrower = (ro(institution, SKOS.narrower))
				if narrower != None:
					narrower_prefLabel = str((ro(narrower, SKOS.prefLabel)))
					valeur = re.search(".*(?= de | de la | d\'A)", narrower_prefLabel)
					if valeur != None:
						# On normalise les caractères
						valeur_group = valeur.group().capitalize()
						valeur_group_decode = unidecode.unidecode(valeur_group)
						if valeur_group_decode not in lst[cle_group_decode]:
							lst[cle_group_decode].append(valeur_group_decode)
							#print(cle_group_decode, institution)


################################################################################
### Villes de la branche "municipalités"
################################################################################

# On récupère le nom des villes
villes = ro_list(URIRef("http://opentheso3.mom.fr/opentheso3/?idc=municipalite&idt=173"), SKOS.narrower)
for ville in villes:
	ville_prefLabel_lower = ro(ville, SKOS.prefLabel)
	ville_prefLabel = ville_prefLabel_lower.upper()
	print(ville_prefLabel)


# On récupère les uuid de ces villes dans lieux.ttl
	query = input_graph_ttl.query("""PREFIX crm: <http://www.cidoc-crm.org/cidoc-crm/>
	PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
	PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
	BASE <http://data-iremus.huma-num.fr/id/>
 
	SELECT ?lieu
	WHERE {
    
        ?lieu a crm:E93_Presence ;
            crm:P1_is_identified_by/rdfs:label ?nom .
            }""", initBindings={"nom":Literal(ville_prefLabel, lang='fr')})

	for result in query:
		print(result)

################################################################################
### Ecriture du json
################################################################################

test = json.dumps(lst, indent=4, ensure_ascii=False)
outputtxt.write(test)
