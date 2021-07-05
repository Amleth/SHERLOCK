import json
import argparse
import os
import sys
import requests
import yaml
from pprint import pprint
import time
import random

# Arguments
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

########################################################################################
## PERSONNES
########################################################################################

r = requests.get(secret["url"] + '/items/personnes?limit=-1&access_token=' + access_token)
print(r)
ids = [item["id"] for item in r.json()["data"]]
r = requests.delete(secret["url"] + '/items/personnes?limit=-1&access_token=' + access_token, json=ids)
print(r)
r = requests.get(secret["url"] + '/items/personnes?limit=-1&access_token=' + access_token)
print(r)
# print(r.json()["data"])

with open(args.json_concepts) as json_file:
	data_concepts = json.load(json_file)
	# random.shuffle(sample)

	pprint(len(data_concepts))

	for i in range(0,len(data_concepts), 50):
		if i == 0:
			continue
		print(i)
		try:
			r = requests.post(secret["url"] + '/items/personnes?access_token=' + access_token, json=data_concepts[i-50:i])
			r.raise_for_status()
		except Exception as e:
			print(e)
		print(r)
		time.sleep(2)

	r = requests.post(secret["url"] + '/items/personnes?access_token=' + access_token, json=data_concepts[5200:5241])
	print(r)


# sys.exit()

########################################################################################
## INDEXATIONS
########################################################################################

r = requests.get(secret["url"] + '/items/sources_articles?limit=-1&access_token=' + access_token)
print(r)
ids = [item["id"] for item in r.json()["data"]]
r = requests.delete(secret["url"] + f'/items/sources_articles?limit=-1&access_token=' + access_token, json=ids)
print(r)
r = requests.get(secret["url"] + '/items/sources_articles?limit=-1&access_token=' + access_token)
print(r)
# print(r.json())

with open(args.json_index) as json_file:
	data_indexation = json.load(json_file)
	# random.shuffle(sample)

	print(len(data_indexation))

	for i in range(0, len(data_indexation), 50):
		if i == 0:
			continue
		print(i)
		try:
			r = requests.post(secret["url"] + '/items/sources_articles?access_token=' + access_token, json=data_indexation[i-50:i])
			r.raise_for_status()
		except Exception as e:
			print(e)
		print(r)
		time.sleep(2)

	r = requests.post(secret["url"] + '/items/sources_articles?access_token=' + access_token, json=data_indexation[1400:1414])
	print(r)