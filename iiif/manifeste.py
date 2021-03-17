import argparse
import json
from tripoli import IIIFValidator
import os
from PIL import Image

parser = argparse.ArgumentParser()
parser.add_argument("--output")
parser.add_argument("--images")
args = parser.parse_args()

count = 0

# Récupération du dossier d'images
for project in os.listdir(args.images):

	path = args.output + "/" + project
	if not os.path.exists(path):
		os.makedirs(path)

	# Données statiques du json
	lst = {
		"@context": "http://iiif.io/api/presentation/2/context.json",
		"@id": f"http://data-iremus.huma-num.fr/iiif/{project}/manifest",
		"@type": "sc:Manifest", "label": f"{project}",
		"sequences": [{
			"@id": f"http://data-iremus.huma-num.fr/iiif/{project}/sequence/normal",
			"@type": "sc:Sequence",
			"canvases": []
		}]
	}

	# Données spécifiques de chaque image
	for image in os.listdir(f"{args.images}/{project}"):
		count += 1
		im = Image.open(f"{args.images}/{project}/{image}")
		width, height = im.size

		lst["sequences"][0]["canvases"].append(
			{
				"@id": f"http://data-iremus.huma-num.fr/iiif/{project}/canvas/{count}",
				"@type": "sc:Canvas",
				"label": f"p. {count}",
				"height": height,
				"width": width,
				"images":[{
					"@context": "http://iiif.io/api/presentation/2/context.json",
					"@id": f"http://data-iremus.huma-num.fr/iiif/{project}/annotation/image",
					"@type": "oa:Annotation",
					"motivation": "sc:painting",
					"resource": {
						"@id": f"http://data-iremus.huma-num.fr/iiif/{project}/{image}.jpg",
						"@type": "dctypes:Image",
						"format": "image/jpeg",
						"height": height,
						"width": width
						},
					"on": f"http://data-iremus.huma-num.fr/iiif/{project}/canvas/{count}"
			}]
		})


	# Dump des données dans un fichier json
	with open(f"{path}/manifeste.json", "w+") as output:
		manifeste = json.dumps(lst, separators=(",", ":"), indent=2, ensure_ascii=False)
		output.write(manifeste)

	# Validation du json NE FONCTIONNE PAS - PROBLEME D'ESPACES
	with open(f"{path}/manifeste.json", "r") as manifeste_test:
		validator = IIIFValidator()
		validator.validate(json.load(manifeste_test))
		validator.print_errors()
