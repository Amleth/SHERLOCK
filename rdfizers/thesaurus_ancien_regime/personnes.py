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
parser.add_argument("--corpus_cache")
args = parser.parse_args()

# CACHE

sys.path.append(str(Path(".").absolute().parent.parent))
from cache_management import get_uuid, read_cache, write_cache  # nopep8

cache_file = str(PurePath.joinpath(Path(".").absolute(), "cache_personnes.yaml"))

# Lecture du cache du corpus
cache_des_uuid_du_corpus = None
with open(args.corpus_cache) as f:
    cache_des_uuid_du_corpus = yaml.load(f, Loader=yaml.FullLoader)

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
# Données statiques
####################################################################################


indexation_regexp = r"MG-[0-9]{4}-[0-9]{2}[a-zA-Z]?_[0-9]{1,3}"

for opentheso_personne_uri, p, o in input_graph.triples((None, RDF.type, SKOS.Concept)):
    dcterms_identifier = str(list(input_graph.objects(opentheso_personne_uri, DCTERMS.identifier))[0])
    E21_uri = she(get_uuid(["personnes", dcterms_identifier, "uuid"]))
    E41_uri = she(get_uuid(["personnes", dcterms_identifier, "E41"]))
    t(E21_uri, a, crm("E21_Person"))
    t(E21_uri, crm("P1_is_identified_by"), E41_uri)
    t(E41_uri, a, crm("E41_Appellation"))
    t(E41_uri, RDFS.label, ro(opentheso_personne_uri, SKOS.prefLabel))
    altLabels = ro_list(opentheso_personne_uri, SKOS.altLabel)
    if len(altLabels) > 0:
        for altLabel in altLabels:
            E41_alt_uri = she(get_uuid(["personnes", dcterms_identifier, "E41_alt", altLabel]))
            t(E41_alt_uri, a, crm("E41_Appellation"))
            t(E41_alt_uri, RDFS.label, altLabel)
            t(E41_uri, crm("P139_has_alternative_form"), E41_alt_uri)
    t(E21_uri, DCTERMS.created, ro(opentheso_personne_uri, DCTERMS.created))
    t(E21_uri, DCTERMS.modified, ro(opentheso_personne_uri, DCTERMS.modified))

    def process_note(p):
        values = ro_list(opentheso_personne_uri, p)
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
                E13_uuid = get_uuid(["personnes", dcterms_identifier, "E13_notes", note_sha1])
                # TODO (2 x P14 : Nathalie & Isabelle)

    for note in [SKOS.editorialNote, SKOS.historyNote, SKOS.note, SKOS.scopeNote]:
        process_note(note)

    exactMatches = ro_list(opentheso_personne_uri, SKOS.exactMatch)
    for exactMatch in exactMatches:
        if exactMatch == "https://opentheso3.mom.fr/opentheso3/index.xhtml":
            continue
        t(E21_uri, SKOS.exactMatch, exactMatch)

    closeMatches = ro_list(opentheso_personne_uri, SKOS.closeMatch)
    for closeMatch in closeMatches:
        t(E21_uri, SKOS.closeMatch, closeMatch)

write_cache(cache_file)
output_graph.serialize(destination=args.outputttl, format="turtle", base="http://data-iremus.huma-num.fr/id/")

sys.exit()

####################################################################################
# Noms
####################################################################################

for opentheso_personne_uri, p, o in input_graph.triples((None, URIRef("http://www.w3.org/2004/02/skos/core#prefLabel"), None)):
    # prefLabel
    D21_uri = URIRef(iremus_ns[str(uuid.uuid4())])
    input_graph.add((D21_uri, RDF.type, URIRef(crmdig_ns["D21_Person_Name"])))
    input_graph.add((D21_uri, RDFS.label, Literal(o)))
    # Attribution du nom
    E13_uri = URIRef(iremus_ns[str(uuid.uuid4())])
    input_graph.add((E13_uri, RDF.type, URIRef(crm_ns["E13_Attribute_Assignement"])))
    input_graph.add((E13_uri, URIRef(crm_ns["P14_carried_out_by"]), URIRef(iremus_ns["899e29f6-43d7-4a98-8c39-229bb20d23b2"])))
    input_graph.add((E13_uri, URIRef(crm_ns["P141_assigned"]), D21_uri))
    input_graph.add((E13_uri, URIRef(crm_ns["P177_assigned_property_type"]), URIRef(iremus_ns["4a673f92-174e-41cb-b0e1-9c32985fa07c"])))  # Identification
    input_graph.add((E13_uri, URIRef(crm_ns["P140_assigned_attribute_to"]), personne))
    if (opentheso_personne_uri, "dcterms:created", o) in input_graph:
        input_graph.add((E13_uri, URIRef(crm_ns["P4_has_time-span"]), Literal(o)))

    # altLabel
for opentheso_personne_uri, p, o in input_graph.triples((None, URIRef("http://www.w3.org/2004/02/skos/core#altLabel"), None)):
    D21_uri = URIRef(iremus_ns[str(uuid.uuid4())])
    input_graph.add((D21_uri, RDFS.label, Literal(o)))
    # Attribution du nom


turtle = input_graph.serialize(format="turtle", base="http://data-iremus.huma-num.fr/id/").decode("utf-8")
print(turtle)
