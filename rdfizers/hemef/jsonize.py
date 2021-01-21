# Prix de precursus ?

import argparse
from collections import defaultdict
import datetime
import json
from openpyxl import load_workbook
from pathlib import Path, PurePath
from pprint import pprint
import sys
import uuid

################################################################################
#
# INIT
#
################################################################################

parser = argparse.ArgumentParser()
parser.add_argument("--xlsx")
parser.add_argument("--divergences")
parser.add_argument("--json")
args = parser.parse_args()

wb = load_workbook(filename=args.xlsx, read_only=True)
ws = wb.active

column_names = {}
for row in ws.rows:
    c = 0
    for cell in row:
        column_names[cell.value] = c
        c += 1
    break

colonnes_divergentes = set()
divergences = defaultdict(lambda: defaultdict(list))
divergences["cursus_parcoursclasse"] = defaultdict(list)
data = {
    "eleves_identifiant_1": defaultdict(dict),
    "classes": defaultdict(dict)
}
nb_lignes_par_eleve = defaultdict(lambda: 0)

# CACHE

sys.path.append(str(Path(".").absolute().parent.parent))
from cache_management import get_uuid, read_cache, write_cache  # nopep8

cache_file = str(PurePath.joinpath(Path(".").absolute(), "cache.yaml"))
read_cache(cache_file)

################################################################################
#
# HELPERS
#
################################################################################

colonnes_inconnues = set()


def r_(row, column_name):
    try:
        v = row[column_names[column_name]]
        if v and type(v) == str:
            v = v.strip()
        elif type(v) == datetime.datetime:
            v = str(v)[:10]
        return v
    except:
        colonnes_inconnues.add(column_name)
        return None

################################################################################
#
# LE BONHEUR EST DANS LE PRÉ
#
################################################################################


# On part du principe que les patronymes sont uniques dans le corps enseignant
professeur_disciplines = defaultdict(set)

i = 0

for row in ws.rows:
    if i == 0:
        i += 1
        continue
    i += 1

    row = [cell.value for cell in row]

    def r(column_name):
        return r_(row, column_name)

    id1 = r('identifiant_1')
    cdc = r("classe_discipline_categorie")
    cdc_tdc = r("classe_discipline_categorie_TDC")
    cn_tdc = r("classe_nom_TDC")
    cnp = r("classe_nom_professeur")
    cnp_tdc = r("classe_nom_professeur_TDC")

    if (cnp or cnp_tdc) and cnp != '?' and cnp_tdc != "?" and (cdc or cdc_tdc or cn_tdc):
        professeur_disciplines[cnp or cnp_tdc].add(cdc or cdc_tdc or cn_tdc)

################################################################################
#
# GO
#
################################################################################

i = 0

for row in ws.rows:
    if i == 0:
        i += 1
        continue
    i += 1
    nb_lignes_par_eleve[row[column_names["identifiant_1"]].value] += 1

i = 0
id_ligne = 0
current_identifiant_1 = None
current_eleve_line = 0

for row in ws.rows:
    if i == 0:
        i += 1
        continue
    i += 1

    row = [cell.value for cell in row]

    def r(column_name):
        return r_(row, column_name)

    def census_divergence(column_name, value):
        colonnes_divergentes.add(column_name)
        if value not in divergences[r('identifiant_1')][column_name]:
            divergences[r('identifiant_1')][column_name].append(value)

    def w(o, must_not_diverge, column_name, data_key):
        value = r(column_name)
        wv(o, must_not_diverge, data_key, column_name, value)

    def wv(o, must_not_diverge, data_key, column_name, value):
        if value and type(value) == str:
            value = value.replace('’', '\'')
        if not value:
            return
        if data_key in o:
            if type(o[data_key]) == str and o[data_key] != value:
                o[data_key] = [o[data_key], value]
                if must_not_diverge:
                    for v in o[data_key]:
                        census_divergence(column_name, v)
            elif type(o[data_key]) == list and value not in o[data_key]:
                o[data_key] = [*o[data_key], value]
                if must_not_diverge:
                    for v in o[data_key]:
                        census_divergence(column_name, v)
        else:
            o[data_key] = value

    if not r("identifiant_1"):
        continue
        # TODO : on en fait quoi ?

    # ÉLÈVE

    if r("identifiant_1") != current_identifiant_1:
        current_identifiant_1 = r("identifiant_1")
        current_eleve_line = 0
    current_eleve_line += 1

    eleve_uuid = get_uuid(["élèves_identifiant_1", r("identifiant_1"), "uuid"])
    eleve = data["eleves_identifiant_1"][r("identifiant_1")]
    eleve["uuid"] = eleve_uuid
    w(eleve, True, "identifiant_1", "identifiant_1")
    w(eleve, True, "identifiant_2", "identifiant_2")
    w(eleve, True, "identifiant_1_TDC", "identifiant_1_TDC")
    w(eleve, True, "eleve_nom", "nom")
    w(eleve, True, "eleve_nom_TDC", "nom_TDC")
    w(eleve, True, "eleve_complement_nom", "nom_complément")
    w(eleve, True, "eleve_nom_epouse", "nom_épouse")
    w(eleve, True, "eleve_nom_epouse_TDC", "nom_épouse_TDC")
    w(eleve, True, "eleve_prenom_1", "prénom_1")
    w(eleve, True, "eleve_prenom_2", "prénom_2")
    w(eleve, True, "eleve_prenom_2_TDC", "prénom_2_TDC")
    w(eleve, True, "eleve_complement_prenom", "prénom_complément")
    w(eleve, True, "eleve_complement_prenom_TDC", "prénom_complément_TDC")
    w(eleve, True, "eleve_pseudonyme", "pseudonyme")
    w(eleve, True, "eleve_pseudonyme_TDC", "pseudonyme_TDC")
    w(eleve, True, "eleve_sexe", "sexe")
    w(eleve, True, "eleve_sexe_TDC", "sexe_TDC")
    w(eleve, True, "eleve_refs_bibliographiques", "références_bibliographiques")
    w(eleve, True, "eleve_cote_AN_registre", "cote_AN_registre")
    w(eleve, True, "eleve_cote_AN_registre_TDC", "cote_AN_registre_TDC")
    w(eleve, True, "eleve_observations", "observations")
    w(eleve, True, "eleve_observations_TDC", "observations_TDC")
    w(eleve, True, "eleve_remarques de saisie", "remarques_de_saisie")
    w(eleve, True, "eleve_remarques de saisie_TDC", "remarques_de_saisie_TDC")

    # NAISSANCE

    w(eleve, True, "eleve_date_naissance", "date_naissance")
    w(eleve, True, "eleve_date_naissance_TDC", "date_naissance_TDC")

    # VILLE DE NAISSANCE

    naissance_ville = eleve["naissance_ville"] if "naissance_ville" in eleve else defaultdict()
    w(naissance_ville, True, "eleve_ville_naissance", "nom")
    w(naissance_ville, True, "eleve_ville_naissance_TDC", "nom_TDC")
    w(naissance_ville, True, "eleve_ville_naissance_ancien_nom", "nom_ancien")
    if "naissance_ville" not in eleve and len(naissance_ville) != 0:
        eleve["naissance_ville"] = naissance_ville

    # DÉPARTEMENT DE NAISSANCE

    naissance_departement = eleve["naissance_département"] if "naissance_département" in eleve else defaultdict()
    w(naissance_departement, True, "eleve_departement_naissance", "nom")
    w(naissance_departement, True, "eleve_departement_naissance_TDC", "nom_TDC")
    if "naissance_département" not in eleve and len(naissance_departement) != 0:
        eleve["naissance_département"] = naissance_departement

    # PAYS DE NAISSANCE

    naissance_pays = eleve["naissance_pays"] if "naissance_pays" in eleve else defaultdict()
    w(naissance_pays, True, "eleve_pays_naissance", "nom")
    w(naissance_pays, True, "eleve_pays_naissance_TDC", "nom_TDC")
    if "naissance_pays" not in eleve and len(naissance_pays) != 0:
        eleve["naissance_pays"] = naissance_pays

    # PÈRE

    pere = eleve["père"] if "père" in eleve else defaultdict()
    w(pere, True, "eleve_profession_pere", "profession")
    w(pere, True, "eleve_profession_pere_TDC", "profession_TDC")
    if "père" not in eleve and len(pere) != 0:
        eleve["père"] = pere

    # MÈRE

    mere = eleve["mère"] if "mère" in eleve else defaultdict()
    w(mere, True, "eleve_profession_mere", "profession")
    w(mere, True, "eleve_profession_mere_TDC", "profession_TDC")
    if "mère" not in eleve and len(mere) != 0:
        eleve["mère"] = mere

    # RECOMMANDATION

    recommandation = eleve["recommandation"] if "recommandation" in eleve else defaultdict()
    w(recommandation, True, "recommandation_date", "date")
    w(recommandation, True, "recommandation_type", "type")
    w(recommandation, True, "recommandation_qualite recommandeur", "qualité_recommandeur")
    if "recommandation" not in eleve and len(recommandation) != 0:
        eleve["recommandation"] = recommandation

    # CURSUS

    w(eleve, True, "cursus_motif_admission", "motif_admission")
    w(eleve, True, "cursus_motif_admission_TDC", "motif_admission_TDC")
    w(eleve, True, "cursus_date_epreuve_admission", "épreuve_admission_date")
    w(eleve, True, "cursus_date_entree_conservatoire", "date_entrée_conservatoire")
    w(eleve, True, "cursus_date_entree_conservatoire_TDC", "date_entrée_conservatoire_TDC")
    w(eleve, True, "cursus_date_sortie_conservatoire", "date_sortie_conservatoire")
    w(eleve, True, "cursus_date_sortie_conservatoire_TDC", "date_sortie_conservatoire_TDC")
    w(eleve, True, "cursus_motif_sortie", "motif_sortie")
    w(eleve, True, "cursus_motif_sortie_TDC", "motif_sortie_TDC")

    # EXERCE + PROFESSION

    exerce = eleve["exerce"] if "exerce" in eleve else defaultdict()
    w(exerce, True, "exerce_distinctions", "distinctions")
    w(exerce, True, "exerce_profession_connue", "profession_connue")
    w(exerce, True, "exerce_profession_connue_TDC", "profession_connue_TDC")
    w(exerce, True, "exerce_date_debut", "date_début")
    w(exerce, True, "exerce_lieu_exercice", "lieu")
    w(exerce, True, "exerce_lieu_exercice_TDC", "lieu_TDC")

    w(exerce, True, "profession_nom", "profession_nom")
    w(exerce, True, "profession_nom_TDC", "profession_nom_TDC")
    w(exerce, True, "profession_secteur", "profession_secteur")

    if "exerce" not in eleve and len(exerce) != 0:
        eleve["exerce"] = exerce

    # PRÉCURSUS

    etablissement_precursus = eleve["établissement_pré-cursus"] if "établissement_pré-cursus" in eleve else defaultdict()
    w(etablissement_precursus, True, "pre-cursus_nom_etablissement", "nom")
    w(etablissement_precursus, True, "pre-cursus_nom_etablissement_TDC", "nom_TDC")
    w(etablissement_precursus, True, "pre-cursus_type_etablissement", "type")
    w(etablissement_precursus, True, "pre-cursus_ville_etablissement", "ville_nom")
    if "établissement_pré-cursus" not in eleve and len(etablissement_precursus) != 0:
        eleve["établissement_pré-cursus"] = etablissement_precursus

    # ADRESSES

    # habite_debut
    # habite_fin

    # adresse_nom_voie
    # adresse_type_voie
    # adresse_article_voie
    # adresse_numero_voie
    # adresse_complements
    # adresse_ville
    # adresse_ville_ancien nom

    # adresse_pays
    # adresse_geolocalisation

    # adresse_nom_voie_TDC
    # adresse_type_voie_TDC
    # adresse_article_voie_TDC
    # adresse_numero_voie_TDC
    # adresse_complements_TDC
    # adresse_ville_TDC
    # adresse_ville_ancien nom_TDC

    adresse_uuid = str(uuid.uuid4())
    adresse = {}
    w(adresse, False, "habite_debut", "habite_début")
    w(adresse, False, "habite_fin", "habite_fin")
    w(adresse, False, "adresse_nom_voie", "nom_voie")
    w(adresse, False, "adresse_nom_voie_TDC", "nom_voie_TDC")
    w(adresse, False, "adresse_type_voie", "type_voie")
    w(adresse, False, "adresse_type_voie_TDC", "type_voie_TDC")
    w(adresse, False, "adresse_article_voie", "article_voie")
    w(adresse, False, "adresse_article_voie_TDC", "article_voie_TDC")
    w(adresse, False, "adresse_numero_voie", "numéro_voie")
    w(adresse, False, "adresse_numero_voie_TDC", "numéro_voie_TDC")
    w(adresse, False, "adresse_complements", "compléments")
    w(adresse, False, "adresse_complements_TDC", "compléments_TDC")
    w(adresse, False, "adresse_ville", "ville_nom")
    w(adresse, False, "adresse_ville_TDC", "ville_nom_TDC")
    w(adresse, False, "adresse_ville_ancien nom", "ville_ancien_nom")
    w(adresse, False, "adresse_ville_ancien nom_TDC", "ville_ancien_nom_TDC")
    w(adresse, False, "adresse_pays", "pays_nom")
    w(adresse, False, "adresse_geolocalisation", "géolocalisation")
    if adresse:
        if "adresses" not in eleve:
            eleve["adresses"] = {}
        if adresse not in eleve["adresses"].values():
            eleve["adresses"][adresse_uuid] = adresse

    # CLASSE

    # DÉMARCHE :
    # Détecter les lignes mixant informations TDC & non TDC.
    # La démarche est de construire une classe, en piochant les infos en non TDC & TDC.
    # Et forger une clef unique.
    #
    # NOTES :
    #   - n'existent pas :
    #     - cdc and cnp and cdc_tdc and cnp_tdc
    #     - cdc and cdc_tdc and cn_tdc

    def print_error(type, msg, data=None):
        return
        print("ERREUR", type, msg, data if data else "", i, id1)

    id1 = r('identifiant_1')
    cdc = r("classe_discipline_categorie")
    cdc_tdc = r("classe_discipline_categorie_TDC")
    cd = r("classe_discipline")
    cn_tdc = r("classe_nom_TDC")
    cnp = r("classe_nom_professeur")
    cnp_tdc = r("classe_nom_professeur_TDC")

    classe_uuid = None
    disc_k = cdc or cdc_tdc or cd
    prof_k = cnp or cnp_tdc

    if not disc_k or not prof_k:
        print_error("CLASSE", f"Classe partiellement définie — discipline :'{disc_k}' ; professeur : '{prof_k}'")

    classe_key = None
    if disc_k and prof_k:
        classe_key = ["classes", disc_k, prof_k]
        classe_uuid = get_uuid(classe_key)
    if not classe_uuid:
        classe_key = ["classes", i]
        classe_uuid = get_uuid(classe_key)

    w(data["classes"][classe_uuid], False, "classe_discipline", "discipline")
    w(data["classes"][classe_uuid], True, "classe_discipline_categorie", "discipline_categorie")
    w(data["classes"][classe_uuid], True, "classe_nom_professeur", "nom_professeur")
    w(data["classes"][classe_uuid], False, "classe_nom_TDC", "nom_TDC")
    w(data["classes"][classe_uuid], True, "classe_discipline_TDC", "discipline_TDC")
    w(data["classes"][classe_uuid], True, "classe_discipline_categorie_TDC", "discipline_categorie_TDC")
    w(data["classes"][classe_uuid], False, "classe_type", "type")
    w(data["classes"][classe_uuid], False, "classe_type_TDC", "type_TDC")
    w(data["classes"][classe_uuid], True, "classe_nom_professeur_TDC", "nom_professeur_TDC")
    w(data["classes"][classe_uuid], False, "classe_observations_TDC", "observations_TDC")
    w(data["classes"][classe_uuid], False, "classes_remarques_saisie", "remarques_saisie")

    if data["classes"][classe_uuid] == dict():
        del data["classes"][classe_uuid]

    # PARCOURS CLASSE

    parcours_classe_uuid = None
    date_entree_k = None

    if r("parcours_classe_date_entree"):
        date_entree_k = r("parcours_classe_date_entree")
    elif r("parcours_classe_date_entree_TDC"):
        date_entree_k = r("parcours_classe_date_entree_TDC")
    else:
        print_error("PARCOURS-CLASSE", "Erreur inconnue.")

    parcours_classe_key = None
    if date_entree_k:
        parcours_classe_key = ["élèves_identifiant_1", r("identifiant_1"), "parcours-classes", classe_uuid, date_entree_k]
        parcours_classe_uuid = get_uuid(parcours_classe_key)
    if not parcours_classe_uuid:
        parcours_classe_key = ["élèves_identifiant_1", r("identifiant_1"), "parcours-classes", classe_uuid, f"ligne_{current_eleve_line}"]
        parcours_classe_uuid = get_uuid(parcours_classe_key)

    if not "parcours-classes" in eleve:
        eleve["parcours-classes"] = {}
    pc = eleve["parcours-classes"][parcours_classe_uuid] if parcours_classe_uuid in eleve["parcours-classes"] else defaultdict()
    w(pc, True, "parcours_classe_statut_eleve", "statut_élève")
    w(pc, True, "parcours_classe_statut_eleve_TDC", "statut_élève_TDC")
    w(pc, True, "parcours_classe_motif_entree", "motif_entrée")
    w(pc, True, "parcours_classe_motif_entree_TDC", "motif_entrée_TDC")
    w(pc, True, "parcours_classe_date_entree", "date_entrée")
    w(pc, True, "parcours_classe_date_entree_TDC", "date_entrée_TDC")
    w(pc, True, "parcours_classe_date_sortie", "date_sortie")
    w(pc, True, "parcours_classe_date_sortie_TDC", "date_sortie_TDC")
    w(pc, True, "parcours_classe_motif_sortie", "motif_sortie")
    w(pc, True, "parcours_classe_motif_sortie_TDC", "motif_sortie_TDC")
    w(pc, True, "parcours_classe_observations_eleve", "observations_élève")
    w(pc, True, "parcours_classe_observations_eleve_TDC", "observations_élève_TDC")
    w(pc, True, "classe_observations", "observations_classe")
    w(pc, True, "classe_cote_AN_TDC", "cote_AN_TDC")
    pc["classe"] = classe_uuid
    if parcours_classe_uuid not in eleve["parcours-classes"] and len(pc) != 0:
        eleve["parcours-classes"][parcours_classe_uuid] = pc

    # PRIX

    prix_key_dict = {
        "élèves_identifiant_1_branch": "élèves_identifiant_1",
        "élève_id": r("identifiant_1"),
        "prix": "prix",
        "discipline_catégorie": r("prix_discipline_categorie") or r("prix_discipline_categorie_TDC"),
        "discipline": r("prix_discipline") or r("prix_discipline_TDC") or "sans_discipline",
        "nom": r("prix_nom") or r("prix_nom_TDC") or "sans_nom",
        "date": r("prix_date") or r("prix_date_TDC") or "sans_date",
        "parcours_classe_date_entrée_valeur": r("parcours_classe_date_entree") or r("parcours_classe_date_entree_TDC")
    }

    def is_empty_prix():
        return list(set([r("prix_rang"), r("prix_date"), r("prix_date_TDC"), r("prix_nom"), r("prix_nom_TDC"), r("prix_nom_complément"), r("prix_nom_complément_TDC"), r("prix_type"), r("prix_type_TDC"), r("prix_discipline"), r("prix_discipline_TDC"), r("prix_discipline_categorie"), r("prix_discipline_categorie_TDC")]))[0] == None

    prix_uuid = None
    prix_key = list(prix_key_dict.values())
    if not is_empty_prix() and parcours_classe_uuid in eleve["parcours-classes"]:
        if None in prix_key:
            prix_key.append(f"ligne_{current_eleve_line}")
        prix_uuid = get_uuid(prix_key)

        if not "prix" in eleve["parcours-classes"][parcours_classe_uuid]:
            eleve["parcours-classes"][parcours_classe_uuid]["prix"] = {}
        prix = eleve["parcours-classes"][parcours_classe_uuid]["prix"][prix_uuid] if prix_uuid in eleve["parcours-classes"][parcours_classe_uuid]["prix"] else defaultdict()
        w(prix, True, "prix_rang", "rang")
        w(prix, True, "prix_date", "date")
        w(prix, True, "prix_date_TDC", "date_TDC")
        w(prix, True, "prix_nom", "nom")
        w(prix, True, "prix_nom_TDC", "nom_TDC")
        w(prix, True, "prix_nom_complément", "nom_complément")
        w(prix, True, "prix_nom_complément_TDC", "nom_complément_TDC")
        w(prix, True, "prix_type", "type")
        w(prix, True, "prix_type_TDC", "type_TDC")
        w(prix, True, "prix_discipline", "discipline")
        w(prix, True, "prix_discipline_TDC", "discipline_TDC")
        w(prix, True, "prix_discipline_categorie", "discipline_categorie")
        w(prix, True, "prix_discipline_categorie_TDC", "discipline_categorie_TDC")
        if prix_uuid not in eleve["parcours-classes"][parcours_classe_uuid]["prix"] and len(prix) != 0:
            eleve["parcours-classes"][parcours_classe_uuid]["prix"][prix_uuid] = prix

################################################################################
#
# CLEAN UP
#
################################################################################

for eleve_id1, v in data["eleves_identifiant_1"].items():
    if v["parcours-classes"] == {}:
        del v["parcours-classes"]

if not divergences["cursus_parcoursclasse"]:
    del divergences["cursus_parcoursclasse"]

################################################################################
#
# THAT'S ALL FOLKS!
#
################################################################################

print('COLONNES INCONNUES', args.xlsx)
pprint(sorted(colonnes_inconnues))

wb.close()

write_cache(cache_file)

for k, v in divergences.items():
    divergences[k]["lignes"] = nb_lignes_par_eleve[k]

divergences["colonnes_divergentes"] = list(colonnes_divergentes)

with open(args.divergences, 'w', encoding='utf-8') as outfile:
    json.dump(divergences, outfile, ensure_ascii=False, indent=4)

with open(args.json, 'w', encoding='utf-8') as outfile:
    json.dump(data, outfile, ensure_ascii=False, indent=4)
