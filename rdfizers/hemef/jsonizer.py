import argparse
from collections import defaultdict
import json
from openpyxl import load_workbook
from pathlib import Path, PurePath
from pprint import pprint
import sys

################################################################################
#
# INIT
#
################################################################################

parser = argparse.ArgumentParser()
parser.add_argument("--xlsx")
parser.add_argument("--divergences")
parser.add_argument("--divergences_cursus_parcoursclasse")
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

divergences = defaultdict(lambda: defaultdict(list))
data = {
    "eleves_identifiant_1": defaultdict(dict),
    "classes": defaultdict(dict)
}
nb_lignes_par_eleve = defaultdict(lambda: 0)

divergences_cursus_parcoursclasse = defaultdict(list)

# CACHE

sys.path.append(str(Path(".").absolute().parent.parent))
from cache_management import get_uuid, read_cache, write_cache  # nopep8

cache_file = str(PurePath.joinpath(Path(".").absolute(), "cache.yaml"))
read_cache(cache_file)

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

for row in ws.rows:
    if i == 0:
        i += 1
        continue
    i += 1

    row = [cell.value for cell in row]

    def r(column_name):
        v = row[column_names[column_name]]
        if v and type(v) == str:
            v = v.strip()
        return v

    def census_divergence(column_name, value):
        if value not in divergences[r('identifiant_1')][column_name]:
            divergences[r('identifiant_1')][column_name].append(value)

    def w(o, must_not_diverge, column_name, data_key):
        value = r(column_name)
        wv(o, must_not_diverge, data_key, column_name, value)

    def wv(o, must_not_diverge, data_key, column_name, value):
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

    def make_adresse(adresse_nom_voie, adresse_type_voie, adresse_article_voie, adresse_numero_voie, adresse_complements):
        if adresse_complements:
            adresse_complements = str(adresse_complements)
        adresse_label = ""
        if adresse_numero_voie:
            adresse_label += str(adresse_numero_voie) + " "
        if adresse_type_voie:
            adresse_label += adresse_type_voie + " "
        if adresse_article_voie:
            adresse_label += adresse_article_voie
            if adresse_article_voie[-1] != "'":
                adresse_label += " "
        if adresse_nom_voie:
            adresse_label += adresse_nom_voie + " "
        if adresse_complements:
            adresse_complements_formatted = adresse_complements
            if adresse_complements[-1] == ")" and "(" not in adresse_complements:
                adresse_complements_formatted = adresse_complements[:-1]
            adresse_label += "[" + adresse_complements_formatted + "]"
        adresse_label = adresse_label.strip()
        return adresse_label

    if not r("identifiant_1"):
        continue
        # TODO : on en fait quoi ?

    # ÉLÈVE

    eleve_uuid = get_uuid(["élèves_identifiant_1", r("identifiant_1"), "uuid"])

    eleve = data["eleves_identifiant_1"][r("identifiant_1")]
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
    w(eleve, True, "eleve_date_naissance", "date_naissance")
    w(eleve, True, "eleve_date_naissance_TDC", "date_naissance_TDC")

    w(eleve, True, "eleve_refs_bibliographiques", "références_bibliographiques")
    w(eleve, True, "eleve_cote_AN_registre", "cote_AN_registre")
    w(eleve, True, "eleve_cote_AN_registre_TDC", "cote_AN_registre_TDC")
    # w(eleve, True, "eleve_observations", "observations")
    # w(eleve, True, "eleve_observations_TDC", "observations_TDC")
    # w(eleve, True, "eleve_remarques de saisie", "remarques_de_saisie")
    # w(eleve, True, "eleve_remarques de saisie_TDC", "remarques_de_saisie_TDC")

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

    w(eleve, True, "cursus_date_epreuve_admission", "épreuve_admission_date")
    w(eleve, True, "cursus_date_entree_conservatoire", "date_entrée_conservatoire")
    w(eleve, True, "cursus_date_entree_conservatoire_TDC", "date_entrée_conservatoire_TDC")
    w(eleve, True, "cursus_date_sortie_conservatoire", "date_sortie_conservatoire")
    w(eleve, True, "cursus_date_sortie_conservatoire_TDC", "date_sortie_conservatoire_TDC")
    for [c, p] in [
        ("cursus_motif_admission", "parcours_classe_motif_entree"),
        ("cursus_motif_admission_TDC", "parcours_classe_motif_entree_TDC"),
        ("cursus_motif_sortie", "parcours_classe_motif_sortie"),
        ("cursus_motif_sortie_TDC", "parcours_classe_motif_sortie_TDC")
    ]:
        cv = r(c)
        pv = r(p)
        if cv and pv and cv != pv:
            dic = dict()
            dic[c] = cv
            dic[p] = pv
            divergences_cursus_parcoursclasse[r("identifiant_1")].append(dic)

    # EXERCE

    exerce = eleve["exerce"] if "exerce" in eleve else defaultdict()
    w(exerce, True, "exerce_distinctions", "distinctions")
    w(exerce, True, "exerce_profession_connue", "profession_connue")
    w(exerce, True, "exerce_profession_connue_TDC", "profession_connue_°TDC")
    w(exerce, True, "exerce_date_debut", "date_début")
    w(exerce, True, "exerce_lieu_exercice", "lieu")
    w(exerce, True, "exerce_lieu_exercice_TDC", "lieu_TDC")
    if "exerce" not in eleve and len(exerce) != 0:
        eleve["exerce"] = exerce

    # PROFESSION

    profession = eleve["profession"] if "profession" in eleve else defaultdict()
    w(profession, True, "profession_nom", "nom")
    w(profession, True, "profession_nom_TDC", "nom_TDC")
    w(profession, True, "profession_secteur", "secteur")
    if "profession" not in eleve and len(profession) != 0:
        eleve["profession"] = profession

    # PRÉCURSUS

    etablissement_precursus = eleve["établissement_pré-cursus"] if "établissement_pré-cursus" in eleve else defaultdict()
    w(etablissement_precursus, True, "pre-cursus_nom_etablissement", "nom")
    w(etablissement_precursus, True, "pre-cursus_nom_etablissement_TDC", "nom_TDC")
    w(etablissement_precursus, True, "pre-cursus_type_etablissement", "type")
    w(etablissement_precursus, True, "pre-cursus_ville_établissement", "ville")
    if "établissement_pré-cursus" not in eleve and len(etablissement_precursus) != 0:
        eleve["établissement_pré-cursus"] = etablissement_precursus

    # ADRESSES

    adresses = eleve["adresses"] if "adresses" in eleve else []
    adresses_TDC = eleve["adresses_TDC"] if "adresses_TDC" in eleve else []
    adresse = {}
    adresse_TDC = {}

    adresse_label = make_adresse(r("adresse_nom_voie"), r("adresse_type_voie"), r("adresse_article_voie"), r("adresse_numero_voie"), r("adresse_complements"))
    adresse_TDC_label = make_adresse(r("adresse_nom_voie_TDC"), r("adresse_type_voie_TDC"), r(
        "adresse_article_voie_TDC"), r("adresse_numero_voie_TDC"), r("adresse_complements_TDC"))
    if adresse_label:
        adresse["label"] = adresse_label
    if adresse_TDC_label:
        adresse_TDC["label"] = adresse_TDC_label
    if r("habite_debut"):
        adresse["habite_début"] = r("habite_debut")
    if r("habite_fin"):
        adresse["habite_fin"] = r("habite_fin")
    if adresse and adresse not in adresses:
        adresses.append(adresse)
    if adresse_TDC and adresse_TDC not in adresses_TDC:
        adresses_TDC.append(adresse_TDC)
    ville = {}
    if r("adresse_ville"):
        ville["nom"] = r("adresse_ville")
    if r("adresse_ville_ancien nom"):
        ville["ancien_nom"] = r("adresse_ville_ancien nom")
    if len(ville) > 0:
        adresse["ville"] = ville
    ville_TDC = {}
    if r("adresse_ville_TDC"):
        ville_TDC["nom"] = r("adresse_ville_TDC")
    if r("adresse_ville_ancien nom_TDC"):
        ville_TDC["ancien_nom"] = r("adresse_ville_ancien nom_TDC")
    if len(ville_TDC) > 0:
        adresse["ville_TDC"] = ville_TDC
    pays = {}
    if r("adresse_pays"):
        pays["nom"] = r("adresse_pays")
    if r("adresse_geolocalisation"):
        pays["géolocalisation"] = r("adresse_geolocalisation")
    if len(pays) > 0:
        adresse["pays"] = pays

    if "adresses" not in eleve and len(adresses) > 0:
        eleve["adresses"] = adresses
    if "adresses_TDC" not in eleve and len(adresses_TDC) > 0:
        eleve["adresses_TDC"] = adresses_TDC

    # PRIX

    # PARCOURS CLASSE

    # AMLETH Dans un premier temps, on n'utilise pas les _TDC du tout.

    # On doit absolument donner une identité à chaque parcours_classe.
    # parcours_classe_uuid = get_uuid(["élèves_identifiant_1", r("identifiant_1"), "pc", r("classe_discipline_categorie")])
    # print(r("identifiant_1"), r("classe_discipline_categorie"), r("classe_nom_professeur"), r("parcours_classe_date_entree"))

    # parcours_classe_statut_eleve
    # parcours_classe_motif_entree
    # parcours_classe_date_entree
    # parcours_classe_date_sortie
    # parcours_classe_motif_sortie
    # parcours_classe_observations_eleve

    # parcours_classe_statut_eleve_TDC
    # parcours_classe_motif_entree_TDC
    # parcours_classe_date_entree_TDC
    # parcours_classe_date_sortie_TDC
    # parcours_classe_motif_sortie_TDC
    # parcours_classe_observations_eleve_TDC

    # CLASSE

    classe_uuid = None
    cdc_v = None
    cnp_v = None

    # DÉMARCHE : Détecter les lignes mixant informations TDC & non TDC. La démarche est de construire une classe, en piochant les infos en non TDC & TDC
    # NOTES :
    #   -  cdc and cnp and cdc_TDC and cnp_TDC n'existe pas

    # Identification des identifiants partiels

    id1 = r('identifiant_1')
    cdc = r("classe_discipline_categorie")
    cnp = r("classe_nom_professeur")
    cdc_tdc = r("classe_discipline_categorie_TDC")
    cnp_tdc = r("classe_nom_professeur_TDC")

    # On recherche d'abord les cas foireux sur lesquels on veut planter
    # Cas où on a 3 valeurs parmis cdc cnp cdc_tdc cnp_tdc
    if cdc and cnp and cdc_tdc and not cnp_tdc:
        print(id1, "cdc & cnp & cdc_tdc & not cnp_tdc")
    elif cdc and cnp and not cdc_tdc and cnp_tdc:
        print(id1, "cdc & cnp & not cdc_tdc & cnp_tdc")
    elif not cdc and cnp and cdc_tdc and cnp_tdc:
        print(id1, "not cdc and cnp and cdc_tdc and cnp_tdc")
    elif cdc and not cnp and cdc_tdc and cnp_tdc:
        print(id1, "cdc and not cnp and cdc_tdc and cnp_tdc")
    # Ensuite on cherche à constituer un id pour la classe
    # elif cdc and cnp:
    #     cdc_v = cdc
    #     cnp_v = cnp
    # elif cdc_tdc and cnp_tdc:
    #     cdc_v = cdc_tdc
    #     cnp_v = cnp_tdc

    # if cdc_v and cnp_v:
    #     classe_uuid = get_uuid(["classes", cdc_v, cnp_v])
    # if not classe_uuid:
    #     print(f"Pas d'UUID de classe généré pour {r('identifiant_1')} (ligne {i}).")

    # r("classe_discipline"),
    # r("classe_discipline_categorie"),
    # r("classe_nom_professeur"),
    # r("classe_nom_TDC"),
    # r("classe_discipline_TDC"),
    # r("classe_discipline_categorie_TDC"),
    # r("classe_type_TDC"),
    # r("classe_nom_professeur_TDC"),
    # r("classe_cote_AN_TDC")

    # data["classes"][classe_uuid]["uuid"] = classe_uuid
    # data["classes"][classe_uuid]["discipline_categorie"] = r("classe_discipline_categorie")
    # data["classes"][classe_uuid]["professeur_nom"] = r("classe_nom_professeur")
    # w(data["classes"][classe_uuid], False, "classe_discipline", "discipline")
    # w(data["classes"][classe_uuid], True, "classes_remarques_saisie", "remarques_saisie")

    # classe_discipline
    # classe_discipline_categorie
    # classe_nom_professeur

    # classe_nom_TDC
    # classe_discipline_TDC
    # classe_discipline_categorie_TDC
    # classe_type_TDC
    # classe_nom_professeur_TDC
    # classe_cote_AN_TDC
    # classe_observations_TDC

################################################################################
#
# THAT'S ALL FOLKS!
#
################################################################################

wb.close()

write_cache(cache_file)

for k, v in divergences.items():
    divergences[k]["lignes"] = nb_lignes_par_eleve[k]

with open(args.divergences, 'w', encoding='utf-8') as outfile:
    json.dump(divergences, outfile, ensure_ascii=False, indent=4)

with open(args.divergences_cursus_parcoursclasse, 'w', encoding='utf-8') as outfile:
    json.dump(divergences_cursus_parcoursclasse, outfile, ensure_ascii=False, indent=4)

with open(args.json, 'w', encoding='utf-8') as outfile:
    json.dump(data, outfile, ensure_ascii=False, indent=4)

# étude du clavier                  'étude du clavier\xa0?', 'étude du clavier'
# trombone                          'trombone', 'trombone à pistons', 'trombone à cylindre'
# trompette                         'trompette à cylindre', 'trompette'
# Harmonie – accompagnement         'harmonie et accompagnement', 'harmonie', 'harmonie et accompagnement pratique'
# étude du clavier                  'clavier', 'étude du clavier'
# Contrepoint – fugue               'composition et contrepoint et fugue', 'composition et contrepoint'
# Harmonie – accompagnement         'harmonie seule', 'harmonie'
# trompette                         'trompette à pistons', 'trompette'
# déclamation dramatique            'déclamation', 'déclamation dramatique'
# saxhorn                           'saxhorn', 'saxhorn en si bémol', 'saxhorn tromba', 'saxhorn en mi bémol', 'saxhorn alto en mi bémol'
# saxophone                         'saxophone alto', 'saxophone basse', 'saxophone', 'saxophone baryton'
