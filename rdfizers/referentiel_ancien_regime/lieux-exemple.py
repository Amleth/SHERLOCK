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
parser.add_argument("--cache_corpus")
args = parser.parse_args()

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


def narrow(id_opentheso, uuid_sherlock):

    # E93_Presence
    t(uuid_sherlock, a, crm("E93_Presence"))

    # E41_Appellation
    E41_uri = she(get_uuid(["lieu", identifier, "E93", "E41"]))
    t(uuid_sherlock, crm("P1_is_identified_by"), E41_uri)
    t(E41_uri, a, crm("E41_Appellation"))
    t(E41_uri, RDFS.label, ro(id_opentheso, SKOS.prefLabel))
    altLabels = ro_list(id_opentheso, SKOS.altLabel)
    if len(altLabels) > 0:
        for altLabel in altLabels:
            E41_alt_uri = she(get_uuid(["lieu", identifier, "E93", "E41_alt", altLabel]))
            t(E41_alt_uri, a, crm("E41_Appellation"))
            t(E41_alt_uri, RDFS.label, altLabel)
            t(E41_uri, crm("P139_has_alternative_form"), E41_alt_uri)

    # DCTERMS.created/modified
    t(uuid_sherlock, DCTERMS.created, ro(id_opentheso, DCTERMS.created))
    t(uuid_sherlock, DCTERMS.modified, ro(id_opentheso, DCTERMS.modified))

    # Les notes

    def process_note(p):
        values = ro_list(id_opentheso, p)
        for v in values:
            if "##id##" in v:
                v = v.split("##id##")
                for v in v:
                    if v:
                        m = re.search(indexation_regexp, v)
                        m_livraison = re.search(indexation_regexp_livraison, v)
                        if m:
                            clef_mercure_livraison = m_livraison.group()
                            clef_mercure_article = m.group()
                            try:
                                F2_article_uri = she(get_uuid(["Corpus", "Livraisons", clef_mercure_livraison, "Expression TEI", "Articles", clef_mercure_article, "F2"], cache_corpus))
                                E13_index_uri = she(get_uuid(["lieu", identifier, "E93", "E13_indexation"]))
                                t(E13_index_uri, a, crm("E13_Attribute_Assignement"))
                                t(E13_index_uri, DCTERMS.created, ro(id_opentheso, DCTERMS.created))
                                t(E13_index_uri, crm("P14_carried_out_by"),
                                  she("899e29f6-43d7-4a98-8c39-229bb20d23b2"))
                                t(E13_index_uri, crm("P14_carried_out_by"),
                                  she("82476bac-cd8a-4bdc-a695-cf90444c9432"))
                                t(E13_index_uri, crm("P140_assigned_attribute_to"), F2_article_uri)
                                t(E13_index_uri, crm("P141_assigned"), uuid_sherlock)
                                t(E13_index_uri, crm("P177_assigned_property_type"), she("c605c8bb-9387-4da1-baec-b0514fd9999c"))

                            except:
                                #print(identifier, clef_mercure_article)
                                pass


            elif "##" in v:
                v = v.split("##")
                for v in v:
                    if v:
                        m = re.search(indexation_regexp, v)
                        m_livraison = re.search(indexation_regexp_livraison, v)
                        if m:
                            clef_mercure_livraison = m_livraison.group()
                            clef_mercure_article = m.group()
                            try:
                                F2_article_uri = she(get_uuid(
                                    ["Corpus", "Livraisons", clef_mercure_livraison, "Expression TEI", "Articles",
                                     clef_mercure_article, "F2"], cache_corpus))
                                E13_index_uri = she(
                                    get_uuid(["lieu", identifier, "E93", "E13_indexation"]))
                                t(E13_index_uri, a, crm("E13_Attribute_Assignement"))
                                t(E13_index_uri, DCTERMS.created, ro(id_opentheso, DCTERMS.created))
                                t(E13_index_uri, crm("P14_carried_out_by"),
                                  she("899e29f6-43d7-4a98-8c39-229bb20d23b2"))
                                t(E13_index_uri, crm("P14_carried_out_by"),
                                  she("82476bac-cd8a-4bdc-a695-cf90444c9432"))
                                t(E13_index_uri, crm("P140_assigned_attribute_to"), F2_article_uri)
                                t(E13_index_uri, crm("P141_assigned"), uuid_sherlock)
                                t(E13_index_uri, crm("P177_assigned_property_type"), she("c605c8bb-9387-4da1-baec-b0514fd9999c"))

                            except:
                                #print(identifier, clef_mercure_article)
                                pass

            else:
                note_sha1_object = hashlib.sha1(v.encode())
                note_sha1 = note_sha1_object.hexdigest()
                E13_uri = she(get_uuid(["lieu", identifier, "E93", "E13"]))
                t(E13_uri, a, crm("E13_Attribute_Assignement"))
                t(E13_uri, DCTERMS.created, ro(id_opentheso, DCTERMS.created))
                t(E13_uri, crm("P14_carried_out_by"), she("899e29f6-43d7-4a98-8c39-229bb20d23b2"))
                t(E13_uri, crm("P14_carried_out_by"),
                  she("82476bac-cd8a-4bdc-a695-cf90444c9432"))
                t(E13_uri, crm("P140_assigned_attribute_to"), uuid_sherlock)
                E13_notes_uri = she(get_uuid(["lieu", identifier, "E93", "E13_notes", note_sha1]))
                t(E13_notes_uri, RDFS.label, Literal(v))
                t(E13_uri, crm("P141_assigned"), E13_notes_uri)
                t(E13_uri, crm("P177_assigned_property_type"), crm("P3_has_note"))

    for note in [SKOS.note, SKOS.historyNote]:
        process_note(note)

    # Exact et Close Matches

    exactMatches = ro_list(id_opentheso, SKOS.exactMatch)
    for exactMatch in exactMatches:
        if exactMatch == "https://opentheso3.mom.fr/opentheso3/index.xhtml":
            continue
        t(uuid_sherlock, SKOS.exactMatch, exactMatch)

    closeMatches = ro_list(id_opentheso, SKOS.closeMatch)
    for closeMatch in closeMatches:
        t(uuid_sherlock, SKOS.closeMatch, closeMatch)

    # Coordonnées géographiques

    E53_uri = she(get_uuid(["lieu", identifier, "E93", "E53"]))
    t(uuid_sherlock, crm("P161_has_spatial_projection"), E53_uri)

    geolat = ro(id_opentheso, URIRef("http://www.w3.org/2003/01/geo/wgs84_pos#lat"))
    geolong = ro(id_opentheso, URIRef("http://www.w3.org/2003/01/geo/wgs84_pos#long"))
    if geolat and geolong:
        t(E53_uri, crm("P168_place_is_defined_by"), l(f"[{str(geolat)}, {str(geolong)}]"))

def explore(id, depth):
	prefLabel = ro(id, SKOS.prefLabel)
	print("    "*depth, prefLabel, id)
	narrowers = ro_list(id, SKOS.narrower)
	for narrower in narrowers:
		explore(narrower, depth+1)


################################################################################
# Lecture du fichier input
################################################################################

explore(URIRef("http://opentheso3.mom.fr/opentheso3/?idc=1336&idt=43"), 0)