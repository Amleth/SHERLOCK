import json
import argparse
import os
import sys
import requests
import yaml
from pprint import pprint

parser = argparse.ArgumentParser()
parser.add_argument("--json_concepts")
parser.add_argument("--json_index")
args = parser.parse_args()

# Secret YAML
file = open(os.path.join(sys.path[0], "secret.yaml"))
secret = yaml.full_load(file)
r = requests.post(secret["url"] + "/auth/login", json={"email": secret["email"], "password": secret["password"]})
access_token = r.json()['data']['access_token']
refresh_token = r.json()['data']['refresh_token']
file.close()

# Test - lecture de données
# r = requests.get(secret["url"] + '/items/sources_articles/MG-1678-01_206?access_token=' + access_token)
# pprint(r.json())
# r = requests.get(secret["url"] + '/items/sources_articles_indices/1?access_token=' + access_token)
# pprint(r.json())
# r = requests.get(secret["url"] + '/items/sources_articles_indices/2?access_token=' + access_token)
# pprint(r.json())

with open(args.json_concepts) as json_file:
	data_concepts = json.load(json_file)

	# pprint(data_concepts)

	r = requests.post(secret["url"] + '/items/personnes?access_token=' + access_token, json=data_concepts[0:1])
	print(r)

with open(args.json_index) as json_file:
	data_index = json.load(json_file)

	r = requests.post(secret["url"] + '/items/sources_articles?access_token=' + access_token, json=data_index)
	print(r)
