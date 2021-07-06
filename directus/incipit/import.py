import argparse
from iremusdocutils import Ikselesix
import json
from datetime import date, datetime
from pprint import pprint
import requests
import yaml
import os
import sys
import time

# Arguments
parser = argparse.ArgumentParser()
parser.add_argument("--xlsx")
parser.add_argument("--json")
args = parser.parse_args()

# Fichier Excel transformé en dictionnaire
xlsx = Ikselesix(args.xlsx)

# Secret YAML
file = open(os.path.join(sys.path[0], "secret.yaml"))
secret = yaml.full_load(file)
r = requests.post(secret["url"] + "/auth/login", json={"email": secret["email"], "password": secret["password"]})
access_token = r.json()['data']['access_token']
refresh_token = r.json()['data']['refresh_token']
file.close()

# Récupération des données du fichier Excel
d = [row for row in xlsx["Sheet1"]]

# Normalisation des clés et des valeurs datetime
def json_serial(obj):
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    raise TypeError ("Type %s not serializable" % type(obj))

for item in d:
    try:
        item["Date de création de la fiche"] = json_serial(item["Date de création de la fiche"])
    except:
        pass
    try:
        item["Date de modification de la fiche"] = json_serial(item["Date de modification de la fiche"])
    except:
        pass
    for k in list(item):
        item[k.replace(" ", "_").replace("é","e").replace("è","e").lower()] = item.pop(k)

# Dump JSON
with open(args.json, 'w', encoding="utf-8") as file:
    json.dump(d, file, ensure_ascii=False)

# Récupération et suppression des données de Directus
r = requests.get(secret["url"] + '/items/incipit?limit=-1&access_token=' + access_token)
print(r)
ids = [item["id"] for item in r.json()["data"]]
r = requests.delete(secret["url"] + '/items/incipit?limit=-1&access_token=' + access_token, json=ids)
print(r)
# print(r.json()["data"])

# r = requests.post(secret["url"] + '/items/incipit?access_token=' + access_token, json={'_id': None,
#  'acte|entree|scene': 'Acte 3',
#  'auteur_de_la_fiche': 'Pascal Denécheau',
#  'chiffrage_de_mesure': '2',
#  'commentaire_sur_la_variante': None,
#  'compositeur': 'Rameau',
#  'cote_de_la_source': 'Vm2.331',
#  'date_de_creation': 1754,
#  'date_de_creation_de_la_fiche': None,
#  'date_de_modification_de_la_fiche': '2008-06-20T16:50:43',
#  'incipit_code': '1 1 1 1 1 176 5432 5',
#  'incipit_litteraire': None,
#  'localisation_dans_la_source': 'p. 84',
#  'notes_et_commentaires': None,
#  'numero_de_la_fiche': 201,
#  'n°_catalogue': 'RCT 32B/3.18',
#  'personnage_chantant': None,
#  'renvoi_1': None,
#  'renvoi_2': None,
#  'renvoi_3': None,
#  "titre_de_l'air": 'Gavotte 1',
#  "titre_de_l'oeuvre": 'Castor et Pollux',
#  "tonalite_de_l'original": 'Mi Majeur',
#  "variante_de_l'incipit": None})

# Envoi du JSON dans Directus
with open(args.json, encoding="utf-8") as json_file:
    data = json.load(json_file)

    # for i in data:
    #     try:
    #         r = requests.post(secret["url"] + '/items/incipit?access_token=' + access_token, json=i)
    #         r.raise_for_status()
    #     except Exception as e:
    #         pprint(i)
    #         print(e)
    #     print(r)


    # Insertion des données du fichier Excel dans Directus
    for i in range(0, len(data), 50):
        if i == 0:
            continue
        print(i)
        try:
            r = requests.post(secret["url"] + '/items/incipit?access_token=' + access_token, json=data[i - 50:i])
            r.raise_for_status()
        except Exception as e:
            print(e)
        print(r)
        time.sleep(1)
