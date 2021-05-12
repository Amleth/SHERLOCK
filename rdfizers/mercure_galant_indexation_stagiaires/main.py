import argparse
import glob
import os
from os import write
import re
from rdflib import Graph, Namespace, DCTERMS, RDF, RDFS, SKOS, URIRef as u, Literal as l
from sherlockcachemanagement import Cache
import yaml
from pathlib import Path
import ntpath

parser = argparse.ArgumentParser()
parser.add_argument("--racine")
parser.add_argument("--input_txt")
parser.add_argument("--output_ttl")
parser.add_argument("--cache_corpus")
parser.add_argument("--cache_personnes")
parser.add_argument("--cache_lieux")
parser.add_argument("--cache_mots_clés")
parser.add_argument("--cache_stagiaires")
parser.add_argument("--cache_institutions")
args = parser.parse_args()

# CACHES

cache_stagiaires = Cache(args.cache_stagiaires)
cache_corpus = Cache(args.cache_corpus)
cache_personnes = Cache(args.cache_personnes)
cache_lieux = Cache(args.cache_lieux)
cache_mots_clés = Cache(args.cache_mots_clés)
cache_institutions = Cache(args.cache_institutions)

################################################################################
# Initialisation des graphes
################################################################################

output_graph = Graph()

crm_ns = Namespace("http://www.cidoc-crm.org/cidoc-crm/")
iremus_ns = Namespace("http://data-iremus.huma-num.fr/id/")
lrmoo_ns = Namespace("http://www.cidoc-crm.org/lrmoo/")

output_graph.bind("crm", crm_ns)
output_graph.bind("dcterms", DCTERMS)
output_graph.bind("lrmoo", lrmoo_ns)
output_graph.bind("she_ns", iremus_ns)

a = RDF.type

def crm(x):
    return u(crm_ns[x])

def lrm(x):
    return u(lrmoo_ns[x])

def she(x):
    return u(iremus_ns[x])

def t(s, p, o):
    output_graph.add((s, p, o))


################################################################################
# CONVERSION DES FICHIERS RTF EN TXT
################################################################################

"""

res = glob.glob(args.racine, recursive=True)
problems = []
clefs = []

i = 1
for f in res:
    try:
        with open(f, 'r') as rtf_file:
            #print('textutil -convert txt ' + f'"{f}"')
            os.system('textutil -convert txt ' + f'"{f}"')
            txt_file_path = f.replace('.rtf', '.txt')
            #print(txt_file_path)
            with open(txt_file_path, 'r') as txt_file:
                lines = txt_file.readlines()
                new_lines = []
                for line in lines:
                    line = line.replace('\n', '').strip()
                    line = line.replace('=', '\t').strip()
                    if not line:
                        continue
                    line_parts = re.split("\t", line)
                    line_parts = [p.strip().replace('  ', ' ') for p in line_parts if p]

                    # Corrections
                    if line_parts[0] == 'lieux concernés':
                        line_parts = 'lieux'
                    if line_parts[0] == 'Lieux':
                        line_parts = 'lieux'
                    if line_parts[0] == 'congrégation':
                        line_parts[0] = 'congrégations'
                    if line_parts[0] == 'Congrégation':
                        line_parts[0] = 'congrégations'
                    if line_parts[0] == 'Congrégations':
                        line_parts[0] = 'congrégations'
                    if line_parts[0] == 'corporation':
                        line_parts[0] = 'corporations'
                    if line_parts[0] == 'corp':
                        line_parts[0] = 'institutions'
                    if line_parts[0] == 'institution':
                        line_parts[0] = 'institutions'
                    if line_parts[0] == 'Institution':
                        line_parts[0] = 'institutions'
                    if line_parts[0] == 'Institutions':
                        line_parts[0] = 'institutions'
                    if line_parts[0] == 'mot clés':
                        line_parts[0] = 'mots clés'
                    if line_parts[0] == 'mot-cle':
                        line_parts[0] = 'mots clés'
                    if line_parts[0] == 'mots—clés':
                        line_parts[0] = 'mots clés'
                    if line_parts[0] == 'Mots clés':
                        line_parts[0] = 'mots clés'
                    if line_parts[0] == 'mots-clés':
                        line_parts[0] = 'mots clés'
                    if line_parts[0] == 'ocite':
                        line_parts[0] = 'oeuvres citées'
                    if line_parts[0] == 'atexte':
                        line_parts[0] = 'personnes'
                    if line_parts[0] == 'Oeuvre cité':
                        line_parts[0] = 'oeuvres citées'
                    if line_parts[0] == 'œuvre citée':
                        line_parts[0] = 'oeuvres citées'
                    if line_parts[0] == 'oeuvre citée':
                        line_parts[0] = 'oeuvres citées'
                    if line_parts[0] == 'personnage':
                        line_parts[0] = 'personnages'
                    if line_parts[0] == 'noms cités':
                        line_parts[0] = 'personnes'
                    if line_parts[0] == 'autr. noms cités':
                        line_parts[0] = 'personnes'
                    if line_parts[0] == 'ncite':
                        line_parts[0] = 'personnes'
                    if line_parts[0] == 'persones':
                        line_parts[0] = 'personnes'
                    if line_parts[0] == 'personne':
                        line_parts[0] = 'personnes'
                    if line_parts[0] == 'Personnes':
                        line_parts[0] = 'personnes'
                    for k in ['congrégations', 'institutions', 'mots clés', 'lieux']:
                        if line_parts[0].startswith(k + ' '):
                            temp = line_parts[0]
                            line_parts[0] = k
                            line_parts.append(temp.replace(k+' ', ''))

                    # Traitement des clefs pourries
                    if line_parts[0] == 'mots' and line_parts[1] == 'clés':
                        line_parts = ['mots clés', *line_parts[2:]]

                    # Recensement des clefs
                    clefs.append(line_parts[0])

                    # Reconstruction de la ligne
                    new_lines.append('='.join(line_parts))
                with open(txt_file_path, 'w') as txt_file:
                    txt_file.write('\n'.join(new_lines))
    except:
        problems.append(f)
    i += 1

print("Fichiers illisibles :", problems)
with open('clefs.txt', 'w') as f:
    f.write('\n'.join(list(sorted(list(set(clefs))))))

"""

################################################################################
# PARSING DES FICHIERS TXT
################################################################################

for file in glob.glob(args.input_txt + '**/*.txt', recursive=True):
    with open(file, "r") as f:
        lines = f.readlines()

        livraison_path = Path(file).parent
        id_livraison = ntpath.basename(livraison_path)
        id_article = ntpath.basename(file)[:-4]

        try:
            article = she(cache_corpus.get_uuid(["Corpus", "Livraisons", id_livraison, "Expression TEI", "Articles", id_article, "F2"]))
        except:
            print(id_article, "(" + id_livraison + "): erreur dans l'id de l'article ou de la livraison")
        else:

            for line in lines:
                if "personnes=" in line:
                    id_personne = line[10:].replace("\n", "")

                    try:
                        uuid_personne = she(cache_personnes.get_uuid(["personnes", id_personne, "uuid"]))
                    except:
                        print(id_article + ": la personne  " + id_personne + "  est introuvable")
                    else:
                        E13_personnes = she(cache_stagiaires.get_uuid(["indexations", "personnes", id_personne, "E13", "uuid"], True))
                        t(E13_personnes, a, crm("E13_Attribute_Assignement"))
                        t(E13_personnes, crm("P14_carried_out_by"), she("684b4c1a-be76-474c-810e-0f5984b47921"))
                        t(E13_personnes, crm("P140_assigned_attribute_to"), article)
                        t(E13_personnes, crm("P141_assigned"), uuid_personne)
                        t(E13_personnes, crm("P177_assigned_property_type"), crm("P67_refers_to"))

                if "lieux=" in line:
                    id_lieu = line[6:].replace("\n", "")

                    try:
                        uuid_lieu = she(cache_lieux.get_uuid(["lieu", id_lieu, "E93", "uuid"]))
                    except:
                        print(id_article + ": le lieu  " + id_lieu + "  est introuvable")
                    else:
                        E13_lieux = she(cache_stagiaires.get_uuid(["indexations", "lieux", id_lieu, "E13", "uuid"], True))
                        t(E13_lieux, a, crm("E13_Attribute_Assignement"))
                        t(E13_lieux, crm("P14_carried_out_by"), she("684b4c1a-be76-474c-810e-0f5984b47921"))
                        t(E13_lieux, crm("P140_assigned_attribute_to"), article)
                        t(E13_lieux, crm("P141_assigned"), uuid_lieu)
                        t(E13_lieux, crm("P177_assigned_property_type"), crm("P67_refers_to"))

                if "institutions=" in line:
                    id_institution = line[13:].replace("\n", "")

                    try:
                        uuid_institution = she(cache_institutions.get_uuid(["institutions et corporations", id_institution, "uuid"]))
                    except:
                        print(id_article + ": l'institution  " + id_institution + "  est introuvable")
                    else:
                        E13_institutions = she(cache_stagiaires.get_uuid(["indexations", "institutions", id_institution, "E13", "uuid"], True))
                        t(E13_institutions, a, crm("E13_Attribute_Assignement"))
                        t(E13_institutions, crm("P14_carried_out_by"), she("684b4c1a-be76-474c-810e-0f5984b47921"))
                        t(E13_institutions, crm("P140_assigned_attribute_to"), article)
                        t(E13_institutions, crm("P141_assigned"), uuid_institution)
                        t(E13_institutions, crm("P177_assigned_property_type"), crm("P67_refers_to"))

                if "mots clés=" in line:
                    id_mots_clé = line[10:].replace("\n", "")

                    try:
                        uuid_mots_clé = she(cache_mots_clés.get_uuid([id_mots_clé]))
                    except:
                        print(id_article + ": le mot-clé  " + id_mots_clé + "  est introuvable ou doit être ajouté au thésaurus")
                    else:
                        E13_mots_clés = she(cache_stagiaires.get_uuid(["indexations", "mots-clés", id_mots_clé, "E13", "uuid"], True))
                        t(E13_mots_clés, a, crm("E13_Attribute_Assignement"))
                        t(E13_mots_clés, crm("P14_carried_out_by"), she("684b4c1a-be76-474c-810e-0f5984b47921"))
                        t(E13_mots_clés, crm("P140_assigned_attribute_to"), article)
                        t(E13_mots_clés, crm("P141_assigned"), uuid_mots_clé)
                        t(E13_mots_clés, crm("P177_assigned_property_type"), crm("P67_refers_to"))

####################################################################################
# ECRITURE DES TRIPLETS
####################################################################################

serialization = output_graph.serialize(format="turtle", base="http://data-iremus.huma-num.fr/id/")
with open(args.output_ttl, "wb") as f:
    f.write(serialization)

cache_stagiaires.bye()
