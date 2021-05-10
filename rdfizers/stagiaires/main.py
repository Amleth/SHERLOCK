import argparse
import glob
import os
from os import write
import re

parser = argparse.ArgumentParser()
parser.add_argument("--racine")
args = parser.parse_args()

res = glob.glob(args.racine, recursive=True)
problems = []
clefs = []

i = 1
for f in res:
    try:
        with open(f, 'r') as rtf_file:
            print('textutil -convert txt ' + f'"{f}"')
            os.system('textutil -convert txt ' + f'"{f}"')
            txt_file_path = f.replace('.rtf', '.txt')
            print(txt_file_path)
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
