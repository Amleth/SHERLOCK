import argparse
import datetime
import json
from openpyxl import load_workbook
from pathlib import Path, PurePath
from rdflib import Graph, Literal, Namespace, DCTERMS, RDF, RDFS, SKOS, URIRef, URIRef as u, Literal, XSD
import re
import sys

################################################################################
#
# INIT
#
################################################################################

parser = argparse.ArgumentParser()
parser.add_argument("--json")
parser.add_argument("--ttl")
args = parser.parse_args()

with open(args.json) as f:
    data = json.load(f)

g = Graph()

crm_ns = Namespace("http://www.cidoc-crm.org/cidoc-crm/")
crmdig_ns = Namespace("http://www.ics.forth.gr/isl/CRMdig/")
hemef_ns = Namespace("http://data-iremus.huma-num.fr/ns/hemef#")
iremus_ns = Namespace("http://data-iremus.huma-num.fr/id/")
lrmoo_ns = Namespace("http://www.cidoc-crm.org/lrmoo/")
sdt_ns = Namespace("http://data-iremus.huma-num.fr/datatypes/")
sherlock_ns = Namespace("http://data-iremus.huma-num.fr/id/")

g.bind("crm", crm_ns)
g.bind("crmdig", crmdig_ns)
g.bind("dcterms", DCTERMS)
g.bind("hemef", hemef_ns)
g.bind("lrmoo", lrmoo_ns)
g.bind("sdt", sdt_ns)

dates_moisies = set()
propriétés_avec_valeurs_composites = set()

################################################################################
#
# RDF HELPERS
#
################################################################################


def crm(x):
    return URIRef(crm_ns[x])


def dig(x):
    return URIRef(crmdig_ns[x])


def t(s, p, o):
    g.add((s, p, o))


def l(v):
    if type(v) == datetime.datetime:
        return Literal(v, datatype=XSD.dateTime)
    elif type(v) == int:
        return Literal(v, datatype=XSD.integer)
    elif type(v) == str:
        return Literal(v)
    else:
        raise Exception(f"Type inconnu : f{v}")

################################################################################
#
# DATA HELPERS
#
################################################################################


MULTIVALUE_SEPARATOR = " ⬢ "  # quelque chose qui n'existera jamais dans les données
UNIFIED_VALUES_PREDICATE_SUFFIX = "_valeur"


def a2l(x):
    if type(x) == list:
        return x
    else:
        return [x]


def join_values(subject, predicate, v, k):
    res = []
    if k in v:
        res.extend(a2l(v[k]))
    res = map(lambda x: str(x), res)
    res = MULTIVALUE_SEPARATOR.join(res)
    if res:
        t(subject, predicate, l(res))


def find_usable_value(data_type, data, subject, field_base_name, predicate_base_name, allow_both_values=False):
    values = []
    if not allow_both_values:
        if field_base_name in data and field_base_name+"_TDC" in data:
            if data[field_base_name] != data[field_base_name+"_TDC"]:
                raise Exception(f"Un {data_type} ne devrait pas avoir `{field_base_name}` & `{field_base_name}_TDC`")
    if field_base_name in data and data[field_base_name]:
        if type(data[field_base_name]) == list:
            raise Exception(f"La propriété {field_base_name} d'un {data_type} ne peut pas être multivaluée.")
        t(subject, hemef_ns[predicate_base_name], l(data[field_base_name]))
        values.append(data[field_base_name])
    if field_base_name+"_TDC" in data and data[field_base_name+"_TDC"]:
        if type(data[field_base_name+"_TDC"]) == list:
            raise Exception(f"La propriété {field_base_name+'_TDC'} d'un {data_type} ne peut pas être multivaluée.")
        t(subject, hemef_ns[predicate_base_name+"_TDC"], l(data[field_base_name+"_TDC"]))
        values.append(data[field_base_name+"_TDC"])
    values = list(set(values))
    if values and len(values) == 1:
        t(subject, hemef_ns[predicate_base_name+UNIFIED_VALUES_PREDICATE_SUFFIX], l(values[0]))
    else:
        t(subject, hemef_ns[predicate_base_name+UNIFIED_VALUES_PREDICATE_SUFFIX], l(values[1]))


def change_TDC_position(predicate, suffix):
    if "_TDC" not in predicate:
        return predicate + suffix
    else:
        predicate = predicate.replace("_TDC", "")
        return predicate + suffix + "_TDC"


def parse_date(x, subject, predicate_base, debug=False):
    t(subject, hemef_ns[change_TDC_position(predicate_base, "_saisie")], l(str(x)))

    if type(x) == int or type(x) == str:
        _ = parse_atom_date(x)
        for date_k, date_v in _.items():
            t(subject, hemef_ns[change_TDC_position(predicate_base, "_" + date_k)], l(date_v))
        if _ != {} and type(x) == str and ('[' in x or ']' in x or '?' in x):
            # Hypothesis
            t(subject, hemef_ns[change_TDC_position(predicate_base, "_hypothèse")], Literal(True, datatype=XSD.boolean))
        pass

    elif type(x) == list:
        dates = [parse_atom_date(d) for d in x if parse_atom_date(d)]

        # We take the min date [TODO discutable…]
        ymd_list = []
        for d in dates:
            ymd = [-1, -1, -1, d]
            if "année" in d:
                ymd[0] = d["année"]
            if "mois" in d:
                ymd[1] = d["mois"]
            if "jour" in d:
                ymd[2] = d["jour"]
            if ymd.count(-1) < 3:
                ymd_list.append(ymd)

        if ymd_list:
            _ = min(ymd_list)[3]
            for date_k, date_v in _.items():
                t(subject, hemef_ns[change_TDC_position(predicate_base, "_" + date_k)], l(date_v))
            # Hypothesis
            t(subject, hemef_ns[change_TDC_position(predicate_base, "_hypothèse")], Literal(True, datatype=XSD.boolean))


def parse_atom_date(v):
    if type(v) == int:
        if v >= 0 and v <= 9999:
            return {"année": v}
        else:
            return {"saisie": str(v)}

    o = {}

    match = re.search(r"([0-9]{4})-?([0-9]{2})?-?([0-9]{2})?", v)
    if match:
        y = int(match.group(1))
        m = match.group(2)
        d = match.group(3)
        o["année"] = y
        if m and int(m):
            m = int(m)
            if 1 <= m <= 12:
                o["mois"] = m
                if d and int(d):
                    d = int(d)
                    try:
                        dt = datetime.datetime(y, m, d)
                        o["jour"] = d
                        o["datetime"] = dt
                    except:
                        dates_moisies.add(v)
    else:
        dates_moisies.add(v)

    return o

################################################################################
#
# CLASSES
#
################################################################################


for classe_uuid, classe in data["classes"].items():
    t(iremus_ns[classe_uuid], RDF.type, hemef_ns["Classe"])

    for k, v in classe.items():
        if k in (
            "discipline",
            "discipline_TDC",
            "nom_TDC",
            "observations",
            "observations_TDC",
            "remarques_saisie",
            "type_TDC"
        ):
            join_values(iremus_ns[classe_uuid], hemef_ns[k], classe, k)
        elif k in ["discipline_categorie", "discipline_categorie_TDC"]:
            find_usable_value("classe", classe, iremus_ns[classe_uuid], "discipline_categorie", "discipline_catégorie")
        elif k in ["nom_professeur", "nom_professeur_TDC"]:
            find_usable_value("classe", classe, iremus_ns[classe_uuid], "nom_professeur", "nom_professeur", True)

################################################################################
#
# ÉLÈVES
#
################################################################################

for eleve_id1, eleve in data["eleves_identifiant_1"].items():
    t(iremus_ns[eleve["uuid"]], RDF.type, hemef_ns["Élève"])

    for k, v in eleve.items():
        if k in [
            "cote_AN_registre",
            "cote_AN_registre_TDC",
            "identifiant_1",
            "identifiant_2",
            "motif_admission",
            "motif_admission_TDC",
            "motif_sortie",
            "motif_sortie_TDC",
            "nom",
            "nom_complément",
            "nom_épouse",
            "nom_épouse_TDC",
            "observations",
            "observations_TDC",
            "prénom_1",
            "prénom_2",
            "prénom_2_TDC",
            "prénom_complément",
            "prénom_complément_TDC",
            "pseudonyme",
            "pseudonyme_TDC",
            "références_bibliographiques",
            "remarques_de_saisie",
            "remarques_de_saisie_TDC"
        ]:
            join_values(iremus_ns[eleve["uuid"]], hemef_ns[k], eleve, k)
        elif k in [
            "date_entrée_conservatoire",
            "date_entrée_conservatoire_TDC",
            "date_naissance",
            "date_naissance_TDC",
            "date_sortie_conservatoire",
            "date_sortie_conservatoire_TDC"
        ]:
            parse_date(v, iremus_ns[eleve["uuid"]], k)
        elif k in ['sexe', 'sexe_TDC']:
            t(iremus_ns[eleve["uuid"]], hemef_ns[k], l({"H": '♂', "F": '♀'}[v]))
        elif k in ["naissance_ville", "naissance_ville_TDC"]:
            for kk, vv in eleve[k].items():
                if kk in ["nom", "nom_TDC"]:
                    find_usable_value("ville", eleve[k], iremus_ns[eleve["uuid"]], "nom", "naissance_ville_nom")
                else:
                    join_values(iremus_ns[eleve["uuid"]], hemef_ns[k+"_"+kk], v, kk)
        elif k in ["naissance_département", "naissance_département_TDC"]:
            for kk, vv in eleve[k].items():
                join_values(iremus_ns[eleve["uuid"]], hemef_ns[k+"_"+kk], v, kk)
        elif k in ["naissance_pays", "naissance_pays_TDC"]:
            for kk, vv in eleve[k].items():
                join_values(iremus_ns[eleve["uuid"]], hemef_ns[k+"_"+kk], v, kk)
        elif k in ["mère", "père"]:
            for kk, vv in v.items():
                join_values(iremus_ns[eleve["uuid"]], hemef_ns[k+"_"+kk], v, kk)
        elif k == "adresses":
            for adresse_uuid, adresse in eleve["adresses"].items():
                t(iremus_ns[eleve["uuid"]], hemef_ns["adresse"], iremus_ns[adresse_uuid])
                for k, v in adresse.items():
                    t(iremus_ns[adresse_uuid], hemef_ns["adresse_"+k], l(v))
        elif k == "exerce":
            for kk, vv in eleve[k].items():
                join_values(iremus_ns[eleve["uuid"]], hemef_ns[k+"_"+kk], v, kk)
        elif k == "établissement_pré-cursus":
            for kk, vv in eleve[k].items():
                join_values(iremus_ns[eleve["uuid"]], hemef_ns[k+"_"+kk], v, kk)
        elif k == "parcours-classes":
            for pc_uuid, pc in v.items():
                t(iremus_ns[eleve["uuid"]], hemef_ns["parcours-classe"], iremus_ns[pc_uuid])
                t(iremus_ns[pc_uuid], hemef_ns["élève"], iremus_ns[eleve["uuid"]])
                t(iremus_ns[pc_uuid], RDF.type, hemef_ns["Parcours-Classe"])
                t(iremus_ns[pc_uuid], hemef_ns["classe"], iremus_ns[pc["classe"]])
                for pc_k, pc_v in pc.items():
                    if pc_k == "classe":
                        continue
                    if pc_k in [
                        "date_entrée",
                        "date_entrée_TDC",
                        "date_sortie",
                        "date_sortie_TDC",
                    ]:
                        parse_date(pc_v, iremus_ns[pc_uuid], pc_k)
                    elif pc_k in [
                        "cote_AN_TDC",
                        "motif_entrée",
                        "motif_entrée_TDC",
                        "motif_sortie",
                        "motif_sortie_TDC",
                        "observations_classe",
                        "observations_élève",
                        "observations_élève_TDC",
                        "statut_élève",
                        "statut_élève_TDC",
                    ]:
                        join_values(iremus_ns[pc_uuid], hemef_ns[pc_k], pc, pc_k)
                    elif pc_k == "prix":
                        for prix_uuid, prix in pc["prix"].items():
                            t(iremus_ns[pc_uuid], hemef_ns["prix"], iremus_ns[prix_uuid])
                            t(iremus_ns[prix_uuid], RDF.type, hemef_ns["Prix"])
                            for prix_k, prix_v in prix.items():
                                if prix_k in [
                                    "nom",
                                    "nom_TDC",
                                    "type",
                                    "type_TDC",
                                    "nom_complément",
                                    "nom_complément_TDC",
                                ]:
                                    find_usable_value("prix", prix, iremus_ns[prix_uuid], prix_k.replace("_TDC", ""), prix_k.replace("_TDC", ""))
                                elif prix_k in ["discipline_categorie", "discipline_categorie_TDC"]:
                                    find_usable_value("prix", prix, iremus_ns[prix_uuid], "discipline_categorie", "discipline_catégorie")
                                else:
                                    join_values(iremus_ns[prix_uuid], hemef_ns[prix_k], prix, prix_k)

################################################################################
#
# THAT'S ALL FOLKS!
#
################################################################################

g.serialize(destination=args.ttl, format="turtle", base="http://data-iremus.huma-num.fr/id/")
