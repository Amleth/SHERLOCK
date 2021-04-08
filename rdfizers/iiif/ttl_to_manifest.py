import argparse
import json
from tripoli import IIIFValidator
import os
from PIL import Image
import sys
from rdflib import Graph
from rdflib.plugins import sparql
from pprint import pprint

parser = argparse.ArgumentParser()
parser.add_argument("--collection_id")
parser.add_argument("--input_ttl")
parser.add_argument("--output_json")
parser.add_argument("--images")
args = parser.parse_args()

output_graph = Graph()
output_graph.load(args.input_ttl, format="turtle")


#################################################################################
## LA COLLECTION
#################################################################################

q = output_graph.query("""
		SELECT ?collection ?coll_label ?page_id ?page_no ?image_id
		
		WHERE {
		
		?collection <http://www.cidoc-crm.org/cidoc-crm/P2_has_type> <http://data-iremus.huma-num.fr/id/14926d58-83e7-4414-90a8-1a3f5ca8fec1> .
		?collection <http://www.cidoc-crm.org/cidoc-crm/P1_is_identified_by> ?coll_E41 .
		?coll_E41 <http://www.w3.org/2000/01/rdf-schema#label> ?coll_label .
		
		OPTIONAL {
		?page a <http://www.cidoc-crm.org/cidoc-crm/E90_Symbolic_Object> .
		?page <http://www.cidoc-crm.org/cidoc-crm/P1_is_identified_by> ?page_E42 . 
		?page_E42 a <http://www.cidoc-crm.org/cidoc-crm/E42_Identifier> .
		?page_E42 <http://www.w3.org/2000/01/rdf-schema#label> ?page_id .
		?page <http://www.cidoc-crm.org/cidoc-crm/P1_is_identified_by> ?page_E41 . 
		?page_E41 a <http://www.cidoc-crm.org/cidoc-crm/E41_Appellation> .
		?page_E41 <http://www.w3.org/2000/01/rdf-schema#label> ?page_no .
		}
		
		OPTIONAL {
		?image a <http://www.cidoc-crm.org/cidoc-crm/E36_Visual_Item> .
		?image_numerisee a <http://www.ics.forth.gr/isl/CRMdig/D1_Digital_Object> ;
		<http://www.cidoc-crm.org/cidoc-crm/P130_shows_features_of> ?image ;
		<http://www.cidoc-crm.org/cidoc-crm/P1_is_identified_by> ?image_E42 .
		?image_E42 a <http://www.cidoc-crm.org/cidoc-crm/E42_Identifier> ;
		<http://www.w3.org/2000/01/rdf-schema#label> ?image_id .
		}
		
		}""")


nom_collection = list(q)[0][1]

lst = {
	"@context": "http://iiif.io/api/presentation/2/context.json",
	"@id": f"http://data-iremus.huma-num.fr/iiif/{args.collection_id}/manifest",
	"@type": "sc:Manifest", "label": f"{nom_collection}",
	"sequences": [{
		"@id": f"http://data-iremus.huma-num.fr/iiif/{args.collection_id}/sequence/normal",
		"@type": "sc:Sequence",
		"canvases": []
	}]
}

#################################################################################
## LES IMAGES
#################################################################################

pages = {}

for resultat in list(q):
	page_id = str(resultat[2])
	page_no = str(resultat[3])
	if page_id != None and page_id not in pages:
		pages.setdefault(page_id, page_no)

			#TODO AJOUTER DIMENSIONS DES IMAGES

for page in sorted(pages):
	lst["sequences"][0]["canvases"].append(
		{
			"@id": f"http://data-iremus.huma-num.fr/iiif/{args.collection_id}/canvas/{page}",
			"@type": "sc:Canvas",
			"label": f"{pages[page]}",
			"height": 0,
			"width": 0,
			"images": [{
				"@context": "http://iiif.io/api/presentation/2/context.json",
				"@id": f"http://data-iremus.huma-num.fr/iiif/{args.collection_id}/annotation/image",
				"@type": "oa:Annotation",
				"motivation": "sc:painting",
				"resource": {
					"@id": f"http://data-iremus.huma-num.fr/iiif/{args.collection_id}/{page}",
					"@type": "dctypes:Image",
					"format": "image/jpeg",
					"height": 0,
					"width": 0
				},
				"on": f"http://data-iremus.huma-num.fr/iiif/{args.collection_id}/canvas/{page}"
			}]
		})

#################################################################################
## DUMP DES DONNEES DANS UN FICHIER JSON
#################################################################################

with open(args.output_json, "r+") as output:
	manifeste = json.dumps(lst, separators=(",", ":"), indent=2, ensure_ascii=False)
	output.write(manifeste)

#################################################################################
## VALIDATION DU MANIFESTE IIIF
#################################################################################

with open(args.output_json, "r") as manifeste_test:
	validator = IIIFValidator()
	validator.validate(json.load(manifeste_test))
	validator.print_errors()
