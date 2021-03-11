import argparse
import json
from tripoli import IIIFValidator
import requests

parser = argparse.ArgumentParser()
parser.add_argument("--output")
# Fichier json test écrit à la main
parser.add_argument("--input")
args = parser.parse_args()

output = open(args.output, "w")

lst = {}
lst.setdefault("@context", "http://data-iremus.huma-num.fr/iiif/context.json")

# Création du json

manifeste = json.dumps(lst, indent=4, ensure_ascii=False)
output.write(manifeste)

# Validation du json test
validator = IIIFValidator()
with open(args.input, "r") as manifeste_test:
	validator.validate(json.load(manifeste_test))
	validator.is_valid
	validator.print_errors()