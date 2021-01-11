import argparse
from collections import defaultdict
import datetime
import json
from openpyxl import load_workbook
from pathlib import Path, PurePath
from pprint import pprint
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
# HELPERS
#
################################################################################

MULTIVALUE_SEPARATOR = " / "
UNIFIED_PREDICATE_SUFFIX = "_valeur"


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


def a2l(x):
    if type(x) == list:
        return x
    else:
        return [x]


def add_tdc(x): return x + " [TDC]"


# Never use it when you loop over keys, you moron!
def join_values_with_tdc(k_base, v):
    res = []
    if k_base in v:
        res.extend(a2l(v[k_base]))
    if f"{k_base}_TDC" in v:
        res.extend(map(add_tdc, a2l(v[f"{k_base}_TDC"])))
    res = MULTIVALUE_SEPARATOR.join(res)
    return res


def deal_with_tdc_fields(data_type, data, subject, field_base_name, predicate_base_name, allow_both_values=False):
    if not allow_both_values:
        if field_base_name in data and field_base_name+"_TDC" in data:
            if data[field_base_name] != data[field_base_name+"_TDC"]:
                raise Exception(f"Un {data_type} ne devrait pas avoir `{field_base_name}` & `{field_base_name}_TDC`")
    if field_base_name in data and data[field_base_name]:
        if type(data[field_base_name]) == list:
            raise Exception(f"La propriété {field_base_name} d'un {data_type} ne peut pas être multivaluée.")
        t(subject, hemef_ns[predicate_base_name], l(data[field_base_name]))
        t(subject, hemef_ns[predicate_base_name+UNIFIED_PREDICATE_SUFFIX], l(data[field_base_name]))
    if field_base_name+"_TDC" in data and data[field_base_name+"_TDC"]:
        if type(data[field_base_name+"_TDC"]) == list:
            raise Exception(f"La propriété {field_base_name+'_TDC'} d'un {data_type} ne peut pas être multivaluée.")
        t(subject, hemef_ns[predicate_base_name+"_TDC"], l(data[field_base_name+"_TDC"]))
        t(subject, hemef_ns[predicate_base_name+UNIFIED_PREDICATE_SUFFIX], l(data[field_base_name+"_TDC"]))


def parse_date(x, subject, predicate_base, debug=False):
    if type(x) == str:
        date_data = parse_atom_date(x)
        for date_k, date_v in date_data.items():
            predicate = predicate_base + "_" + date_k
            t(subject, hemef_ns[predicate], l(date_v))
    elif type(x) == list:
        dates = list(filter(lambda x: True if x else False, map(parse_atom_date, x)))
        dates = [parse_atom_date(d) for d in x if parse_atom_date(d)]
        for date_part_k in ["année", "mois", "jour"]:
            try:
                date_part_v = min(list(map(lambda x: x[date_part_k], dates)))  # discutable…
                predicate = predicate_base + "_" + date_part_k
                t(subject, hemef_ns[predicate], l(date_part_v))
            except:
                pass
    elif type(x) == int:
        t(subject, hemef_ns[predicate_base + "_année"], l(x))


def parse_atom_date(v):
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


def format_exerce(v):
    # date_début
    # lieu
    # lieu_TDC
    # profession_connue
    # profession_connue_TDC
    profession_connue = MULTIVALUE_SEPARATOR.join(a2l(v["profession_connue"])) if "profession_connue" in v else ""
    profession_connue_TDC = MULTIVALUE_SEPARATOR.join(map(add_tdc, a2l(v["profession_connue_TDC"]))) if "profession_connue_TDC" in v else ""
    profession_connue = MULTIVALUE_SEPARATOR.join([x for x in [profession_connue, profession_connue_TDC] if x])
    lieu = MULTIVALUE_SEPARATOR.join(a2l(v["lieu"])) if "lieu" in v else ""
    lieu_TDC = MULTIVALUE_SEPARATOR.join(map(add_tdc, a2l(v["lieu_TDC"]))) if "lieu_TDC" in v else ""
    lieu = MULTIVALUE_SEPARATOR.join([x for x in [lieu, lieu_TDC] if x])
    date_début = MULTIVALUE_SEPARATOR.join(map(str, a2l(v["date_début"]))) if "date_début" in v else ""
    exerce = profession_connue
    if lieu:
        if exerce:
            exerce += " — "
        exerce += "Lieu : " + lieu
    if date_début:
        if exerce:
            exerce += " — "
        exerce += "Depuis : " + date_début
    return exerce


def format_pré_cursus(v):
    # nom
    # nom_TDC
    # type
    # ville
    précursus = ""
    if "nom" in v:
        précursus += v["nom"]
    if "nom_TDC" in v:
        if "nom" in v:
            précursus += MULTIVALUE_SEPARATOR
        précursus += add_tdc(v["nom_TDC"])
    if "type" in v:
        if précursus:
            précursus += " "
        précursus += f"({v['type']})"
    if "ville" in v:
        if précursus:
            précursus += ", "
        précursus += v["ville"]
    return précursus


def format_profession_parent(v):
    # profession
    # profession_TDC
    profession = a2l(v["profession"]) if "profession" in v else ""
    profession_TDC = map(add_tdc, a2l(v["profession_TDC"])) if "profession_TDC" in v else ""
    return MULTIVALUE_SEPARATOR.join([*profession, *profession_TDC])

################################################################################
#
# CLASSES
#
################################################################################


for classe_uuid, classe in data["classes"].items():
    t(iremus_ns[classe_uuid], RDF.type, hemef_ns["Classe"])

    # observations
    # observations_TDC
    # remarques_saisie
    for k in ("observations", "remarques_saisie"):
        o = join_values_with_tdc(k, classe)
        if o:
            t(iremus_ns[classe_uuid], hemef_ns[k], l(o))

    # discipline_categorie & discipline_categorie_TDC
    deal_with_tdc_fields("classe", classe, iremus_ns[classe_uuid], "discipline_categorie", "discipline_catégorie")
    deal_with_tdc_fields("classe", classe, iremus_ns[classe_uuid], "nom_professeur", "nom_professeur", True)

    for k in ("discipline",
              "discipline_TDC",
              "nom_TDC",
              "type_TDC"):
        if k not in classe:
            continue
        v = classe[k]
        if type(v) == str:
            t(iremus_ns[classe_uuid], hemef_ns[k], l(v))
        elif type(v) == list:
            v = MULTIVALUE_SEPARATOR.join(v)
            t(iremus_ns[classe_uuid], hemef_ns[k], l(v))
        else:
            raise Exception(f"Type d'objet inconnu sur la classe `{classe_uuid}` pour le prédicat `{k}` : `{v}`")

################################################################################
#
# ÉLÈVES
#
################################################################################

for eleve_id1, eleve in data["eleves_identifiant_1"].items():
    t(iremus_ns[eleve["uuid"]], RDF.type, hemef_ns["Élève"])

    for k in ("motif_sortie", "motif_admission", "observations", "remarques_de_saisie"):
        o = join_values_with_tdc(k, eleve)
        if o:
            t(iremus_ns[eleve["uuid"]], hemef_ns[k], l(o))

    for k, v in eleve.items():

        if k in ("motif_sortie", "motif_admission", "observations", "remarques_de_saisie", "motif_sortie_TDC", "motif_admission_TDC", "observations_TDC", "remarques_de_saisie_TDC"):
            continue

        if k in ("date_entrée_conservatoire", "date_entrée_conservatoire_TDC", "date_naissance", "date_naissance_TDC", "date_sortie_conservatoire", "date_sortie_conservatoire_TDC"):
            parse_date(v, iremus_ns[eleve["uuid"]], k)

        else:

            # Clefs scalaires
            if type(v) == str:
                t(iremus_ns[eleve["uuid"]], hemef_ns[k], l(v))

            # Clefs composites
            elif type(v) == list:
                propriétés_avec_valeurs_composites.add(k)
                if k in ["adresses", "adresses_TDC"]:
                    for adresse in v:
                        if "label" in adresse:
                            t(iremus_ns[eleve["uuid"]], hemef_ns["adresse_label"], l(adresse["label"]))
                        for k_ville in ["ville", "ville_TDC"]:
                            if k_ville in adresse:
                                for k in adresse[k_ville]:
                                    t(iremus_ns[eleve["uuid"]], hemef_ns["adresse_"+k_ville+"_"+k], l(adresse[k_ville][k]))
                else:
                    t(iremus_ns[eleve["uuid"]], hemef_ns[k], l(MULTIVALUE_SEPARATOR.join(v)))

            # Entités liées
            # mère
            # naissance_département
            # naissance_pays
            # naissance_ville
            # parcours-classes
            # profession
            # père
            # établissement_pré-cursus
            elif type(v) == dict:
                if k == "exerce":
                    exerce = format_exerce(v)
                    if exerce:
                        t(iremus_ns[eleve["uuid"]], hemef_ns["exerce"], l(exerce))
                elif k == "père":
                    pp = format_profession_parent(v)
                    if pp:
                        t(iremus_ns[eleve["uuid"]], hemef_ns["père_profession"], l(pp))
                elif k == "mère":
                    pp = format_profession_parent(v)
                    if pp:
                        t(iremus_ns[eleve["uuid"]], hemef_ns["mère_profession"], l(pp))
                elif k == "naissance_département":
                    deal_with_tdc_fields("élève", v, iremus_ns[eleve["uuid"]], "nom", "naissance_département")
                elif k == "naissance_pays":
                    deal_with_tdc_fields("élève", v, iremus_ns[eleve["uuid"]], "nom", "naissance_pays")
                elif k == "naissance_ville":
                    if "nom_ancien" in v:
                        t(iremus_ns[eleve["uuid"]], hemef_ns["naissance_ville_ancien_nom"], l(v["nom_ancien"]))
                    deal_with_tdc_fields("élève", v, iremus_ns[eleve["uuid"]], "nom", "naissance_ville")
                elif k == "établissement_pré-cursus":
                    précursus = format_pré_cursus(v)
                    if précursus:
                        t(iremus_ns[eleve["uuid"]], hemef_ns["établissement_pré-cursus"], l(précursus))
                elif k == "parcours-classes":
                    for pc_uuid, pc in v.items():
                        t(iremus_ns[eleve["uuid"]], hemef_ns["parcours-classe"], iremus_ns[pc_uuid])
                        t(iremus_ns[pc_uuid], RDF.type, hemef_ns["Parcours-Classe"])
                        t(iremus_ns[pc_uuid], hemef_ns["classe"], iremus_ns[pc["classe"]])

                        # date_entrée
                        # date_entrée_TDC
                        # date_sortie
                        # date_sortie_TDC
                        for kk, vv in pc.items():
                            if kk in ("date_entrée", "date_entrée_TDC", "date_sortie", "date_sortie_TDC"):
                                date_data = parse_date(vv, iremus_ns[pc_uuid], kk)

                        # motif_entrée
                        # motif_entrée_TDC
                        # motif_sortie
                        # motif_sortie_TDC
                        for _ in ("motif_entrée", "motif_sortie"):
                            o = join_values_with_tdc(_, pc)
                            if o:
                                t(iremus_ns[pc_uuid], hemef_ns[_], l(o))

                        # observations_élève
                        # observations_élève_TDC
                        o = join_values_with_tdc("observations_élève", pc)
                        if o:
                            t(iremus_ns[pc_uuid], hemef_ns["observations_élève"], l(o))

                        # statut_élève
                        # statut_élève_TDC
                        # TODO deal_with_tdc_fields ?
                        o = join_values_with_tdc("statut_élève", pc)
                        if o:
                            t(iremus_ns[pc_uuid], hemef_ns["statut_élève"], l(o))

                        # cote_AN_TDC
                        o = join_values_with_tdc("cote_AN_TDC", pc)
                        if o:
                            t(iremus_ns[pc_uuid], hemef_ns["cote_AN"], l(o))

                        # prix
                        if "prix" in pc:
                            for prix_uuid, prix in pc["prix"].items():
                                t(iremus_ns[pc_uuid], hemef_ns["prix"], iremus_ns[prix_uuid])
                                t(iremus_ns[prix_uuid], RDF.type, hemef_ns["Prix"])

                                # discipline_categorie & discipline_categorie_TDC
                                deal_with_tdc_fields("prix", prix, iremus_ns[prix_uuid], "discipline_categorie", "discipline_catégorie")

                                # date & date_TDC
                                for k in ["date", "date_TDC"]:
                                    if k in prix:
                                        parse_date(prix[k], iremus_ns[prix_uuid], "date", debug=True)

                                # discipline & discipline_TDC
                                deal_with_tdc_fields("prix", prix, iremus_ns[prix_uuid], "discipline", "discipline")

                                # nom & nom_TDC
                                deal_with_tdc_fields("prix", prix, iremus_ns[prix_uuid], "nom", "nom")

                                # nom_complément & nom_complément_TDC
                                deal_with_tdc_fields("prix", prix, iremus_ns[prix_uuid], "nom_complément", "nom_complément")

                                # rang
                                if "rang" in prix:
                                    t(iremus_ns[prix_uuid], hemef_ns["rang"], l(prix["rang"]))

                                # type & type_TDC
                                deal_with_tdc_fields("prix", prix, iremus_ns[prix_uuid], "type", "type")
                                pass
            else:
                raise Exception("???")

################################################################################
#
# THAT'S ALL FOLKS!
#
################################################################################

g.serialize(destination=args.ttl, format="turtle", base="http://data-iremus.huma-num.fr/id/")
