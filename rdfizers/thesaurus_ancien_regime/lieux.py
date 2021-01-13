import argparse
import hashlib
import os
from pathlib import Path, PurePath
from types import prepare_class
from rdflib import Graph, Literal, Namespace, DCTERMS, RDF, RDFS, SKOS, URIRef, URIRef as u, Literal as l
import re
import sys
import uuid
import yaml

parser = argparse.ArgumentParser()
parser.add_argument("--inputrdf")
parser.add_argument("--outputttl")
parser.add_argument("--cache_lieux")
args = parser.parse_args()

# CACHE

sys.path.append(str(Path(".").absolute().parent.parent))
from cache_management import get_uuid, read_cache, write_cache  # nopep8

cache_file = str(PurePath.joinpath(Path(".").absolute(), "cache_lieux.yaml"))

# Lecture du cache
cache_des_uuid_du_thesaurus_lieux = None
with open(args.cache_lieux) as f:
    cache_des_uuid_du_thesaurus_lieux = yaml.load(f, Loader=yaml.FullLoader)

################################################################################
# Initialisation des graphes
################################################################################

input_graph = Graph()
input_graph.load(args.inputrdf)

output_graph = Graph()

crm_ns = Namespace("http://www.cidoc-crm.org/cidoc-crm/")
crmdig_ns = Namespace("http://www.ics.forth.gr/isl/CRMdig/")
iremus_ns = Namespace("http://data-iremus.huma-num.fr/id/")
lrmoo_ns = Namespace("http://www.cidoc-crm.org/lrmoo/")
sdt_ns = Namespace("http://data-iremus.huma-num.fr/datatypes/")

output_graph.bind("crm", crm_ns)
output_graph.bind("crmdig", crmdig_ns)
output_graph.bind("dcterms", DCTERMS)
output_graph.bind("lrmoo", lrmoo_ns)
output_graph.bind("sdt", sdt_ns)

a = RDF.type


def crm(x):
    return URIRef(crm_ns[x])


def dig(x):
    return URIRef(crmdig_ns[x])


def lrm(x):
    return URIRef(lrmoo_ns[x])


def she(x):
    return URIRef(iremus_ns[x])


def t(s, p, o):
    output_graph.add((s, p, o))


def ro(s, p):
    try:
        return list(input_graph.objects(s, p))[0]
    except:
        return None


def ro_list(s, p):
    try:
        return list(input_graph.objects(s, p))
    except:
        return None

####################################################################################
# DONNEES STATIQUES
####################################################################################

indexation_regexp = r"MG-[0-9]{4}-[0-9]{2}[a-zA-Z]?_[0-9]{1,3}"

E32_ancien_regime_uri = URIRef(iremus_ns["b18e2fad-4827-4533-946a-1b9914df6e18"])
E32_lieux_uri = URIRef(iremus_ns["4e7cdc71-b834-412a-8cab-daa363a8334e"])
t(E32_ancien_regime_uri, a, crm("E32_Authority_Document"))
t(E32_ancien_regime_uri, crm("P1_is_identified_by"), Literal("Ancien Régime"))
t(E32_ancien_regime_uri, crm("P71_lists"), E32_lieux_uri)
t(E32_lieux_uri, a, crm("E32_Authority_Document"))
t(E32_lieux_uri, crm("P1_is_identified_by"), Literal("Noms de lieux"))

####################################################################################
# LIEUX
####################################################################################

for opentheso_lieu_uri, p, o in input_graph.triples((None, RDF.type, SKOS.Concept)):
    identifier = ro(opentheso_lieu_uri, DCTERMS.identifier)
    E93_uri = she(get_uuid(["lieu", identifier, "E93", "uuid"]))
    t(E93_uri, a, crm("E93_Presence"))
    t(E32_lieux_uri, crm("P71_lists"), E93_uri)
    E41_uri = she(get_uuid(["lieu", identifier, "E93", "E41"]))
    t(E93_uri, crm("P1_is_identified_by"), E41_uri)
    t(E41_uri, a, crm("E41_Appellation"))
    t(E41_uri, RDFS.label, ro(opentheso_lieu_uri, SKOS.prefLabel))
    altLabels = ro_list(opentheso_lieu_uri, SKOS.altLabel)
    if len(altLabels) > 0:
        for altLabel in altLabels:
            E41_alt_uri = she(get_uuid(["lieu", identifier, "E93", "E41_alt", altLabel]))
            t(E41_alt_uri, a, crm("E41_Appellation"))
            t(E41_alt_uri, RDFS.label, altLabel)
            t(E41_uri, crm("P139_has_alternative_form"), E41_alt_uri)
    t(E93_uri, DCTERMS.created, ro(opentheso_lieu_uri, DCTERMS.created))
    t(E93_uri, DCTERMS.modified, ro(opentheso_lieu_uri, DCTERMS.modified))

    def process_note(p):
        values = ro_list(opentheso_lieu_uri, p)
        for v in values:
            if "##id##" in v:
                v = v.split("##id##")
                for v in v:
                    if v:
                        m = re.search(indexation_regexp, v)
                        if m:
                            clef_mercure = m.group()
                            # Un truc du genre F2_article_uuid = get_uuid(["F2", "article", clef_mercure], cache_des_uuid_du_corpus)
            elif "##" in v:
                v = v.split("##")
                for v in v:
                    if v:
                        m = re.search(indexation_regexp, v)
                        if m:
                            clef_mercure = m.group()
                            # TODO, comme en haut

            else:
                note_sha1_object = hashlib.sha1(v.encode())
                note_sha1 = note_sha1_object.hexdigest()
                E13_uri = she(get_uuid(["lieu", identifier, "E93", "E13"]))
                t(E13_uri, a, crm("E13_Attribute_Assignement"))
                t(E13_uri, crm("P14_carried_out_by"), she("899e29f6-43d7-4a98-8c39-229bb20d23b2"))
                t(E13_uri, crm("P140_assigned_attribute_to"), E93_uri)
                E13_notes_uri = she(get_uuid(["lieu", identifier, "E93", "E13_notes", note_sha1]))
                t(E13_notes_uri, RDFS.label, Literal(v))
                t(E13_uri, crm("P141_assigned"), E13_notes_uri)
                t(E13_uri, crm("P177_assigned_property_type"), crm("P3_has_note"))

    for note in [SKOS.note]:
        process_note(note)

#Ne pas oublier closematch et exactMatch

write_cache(cache_file)
output_graph.serialize(destination=args.outputttl, format="turtle", base="http://data-iremus.huma-num.fr/id/")