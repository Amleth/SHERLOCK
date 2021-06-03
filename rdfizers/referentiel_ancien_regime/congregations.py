import argparse
from rdflib.plugins import sparql
from rdflib import Graph, Literal, Namespace, DCTERMS, RDF, RDFS, SKOS, URIRef, URIRef as u, Literal as l
import xlsxwriter
import uuid
import yaml
from sherlockcachemanagement import Cache
import re
import hashlib
import io
import sys
from pprint import pprint


def norm_label(l):
    return re.sub(r"(\s\[.*)|(\s\(.*)", " ", l).strip().lower().replace("é", "e").replace("è", "e").replace("â", "a")


parser = argparse.ArgumentParser()
parser.add_argument("--input_rdf")
parser.add_argument("--output_ttl")
parser.add_argument("--cache_congregations")
parser.add_argument("--cache_corpus")
parser.add_argument("--cache_lieux_uuid")
parser.add_argument("--situation_geo")
args = parser.parse_args()

# CACHE

cache_corpus = Cache(args.cache_corpus)
cache_congregations = Cache(args.cache_congregations)

cache_lieux_uuid_yaml = None
with open(args.cache_lieux_uuid, "r", encoding="utf-8") as file:
    cache_lieux_uuid_yaml = yaml.load(file, Loader=yaml.FullLoader)

cache_lieux_uuid_yaml_normalisé = {}
for cle in cache_lieux_uuid_yaml.keys():
    lieu = norm_label(cle)
    cache_lieux_uuid_yaml_normalisé[lieu] = cache_lieux_uuid_yaml[cle]

id_congrégations_à_aligner= []
with open(args.situation_geo, "r+", encoding="utf-8") as f:
    id_congrégations_à_aligner = f.read()

##################################################################################
# INITIALISATION DES GRAPHES
##################################################################################

input_graph = Graph()
input_graph.load(args.input_rdf)

output_graph = Graph()

crm_ns = Namespace("http://www.cidoc-crm.org/cidoc-crm/")
iremus_ns = Namespace("http://data-iremus.huma-num.fr/id/")
lrmoo_ns = Namespace("http://www.cidoc-crm.org/lrmoo/")
sdt_ns = Namespace("http://data-iremus.huma-num.fr/datatypes/")
sherlock_ns = Namespace("http://data-iremus.huma-num.fr/ns/sherlock#")

output_graph.bind("crm", crm_ns)
output_graph.bind("dcterms", DCTERMS)
output_graph.bind("lrmoo", lrmoo_ns)
output_graph.bind("sdt", sdt_ns)
output_graph.bind("skos", SKOS)
output_graph.bind("she_ns", sherlock_ns)

a = RDF.type

##################################################################################
#
##################################################################################

# Normalisation des labels de congrégations pour préparer l'alignement
noms_de_congrégations_normalisés = {}
prefLabels = input_graph.query('''
SELECT ?id ?prefLabel ?altLabel
WHERE {
    ?s <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://www.w3.org/2004/02/skos/core#Concept> .
    OPTIONAL { ?s <http://www.w3.org/2004/02/skos/core#prefLabel> ?prefLabel } .
    OPTIONAL { ?s <http://www.w3.org/2004/02/skos/core#altLabel> ?altLabel } .
    OPTIONAL { ?s <http://purl.org/dc/terms/identifier> ?id }
}
''')


for t in prefLabels:
    t = (norm_label(str(t[0])) if t[0] else None, norm_label(str(t[1])) if t[1] else None, norm_label(str(t[2])) if t[2] else None)
    if t[0] not in noms_de_congrégations_normalisés:
        noms_de_congrégations_normalisés[t[0]] = []
    if t[1]:
        if t[1] not in noms_de_congrégations_normalisés[t[0]]:
            noms_de_congrégations_normalisés[t[0]].append(t[1])
    if t[2]:
        if t[2] not in noms_de_congrégations_normalisés[t[0]]:
            noms_de_congrégations_normalisés[t[0]].append(t[2])


##################################################################################
# FONCTIONS
##################################################################################


def crm(x):
    return URIRef(crm_ns[x])


def lrm(x):
    return URIRef(lrmoo_ns[x])


def she(x):
    return URIRef(iremus_ns[x])

def she_ns(x):
    return URIRef(sherlock_ns[x])


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


def count_concepts():
    q = input_graph.query(
        """
        SELECT (COUNT(?concept) AS ?n)
        WHERE {
            ?concept <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://www.w3.org/2004/02/skos/core#Concept> .
        }
        """)
    return int(list(q)[0][0])

#print(f"{count_concepts()} concepts à traiter")


def explore(concept, depth):

    identifier = ro(concept, DCTERMS.identifier)
    E74_uri = she(cache_congregations.get_uuid(["congregations", identifier, "uuid"], True))
    t(F34_congregations_uri, crm("P71_lists"), E74_uri)
    t(E74_uri, a, crm("E74_Group"))

    # IDENTIFIER OPENTHESO
    E42_uri = she(cache_congregations.get_uuid(["congregations", identifier, "E42_opentheso"], True))
    t(E42_uri, a, crm("E42_Identifier"))
    t(E74_uri, crm("P1_is_identified_by"), E42_uri)
    t(E42_uri, RDFS.label, Literal(identifier))

    # APPELLATION
    E41_uri = she(cache_congregations.get_uuid(["congregations", identifier, "E41"], True))
    t(E74_uri, crm("P1_is_identified_by"), E41_uri)
    t(E41_uri, a, crm("E41_Appellation"))
    for prefLabel in ro_list(concept, SKOS.prefLabel):
        t(E41_uri, RDFS.label, prefLabel)

    altLabels = ro_list(concept, SKOS.altLabel)
    if len(altLabels) > 0:
        for altLabel in altLabels:
            E41_alt_uri = she(cache_congregations.get_uuid(["congregations", identifier, "E41_alt", altLabel], True))
            t(E41_alt_uri, a, crm("E41_Appellation"))
            t(E41_alt_uri, RDFS.label, altLabel)
            t(E41_uri, crm("P139_has_alternative_form"), E41_alt_uri)

    # ALIGNEMENT AU REFERENTIEL DES LIEUX
    if identifier in id_congrégations_à_aligner:
        for label in noms_de_congrégations_normalisés[str(identifier).lower()]:
            for lieu in cache_lieux_uuid_yaml_normalisé.keys():
                if label.endswith(" " + lieu) or label.endswith("'"+lieu) or label.endswith(" de "+lieu) or label.endswith(" a "+lieu) or label.endswith(" du "+lieu) or label.endswith(" le "+lieu) or label.endswith(" la "+lieu) or label.endswith(" à "+lieu):
                    lieu_uuid = cache_lieux_uuid_yaml_normalisé[lieu][0]
                    t(E74_uri, she_ns("sheP_situation_géohistorique"), she(lieu_uuid))

    # E13 INDEXATION

    def process_note(p):
        indexation_regexp = r"MG-[0-9]{4}-[0-9]{2}[a-zA-Z]?_[0-9]{1,3}"
        indexation_regexp_livraison = r"MG-[0-9]{4}-[0-9]{2}[a-zA-Z]?"
        values = ro_list(concept, p)
        for v in values:
            if "##id##" in v:
                v = v.split("##id##")
                for v in v:
                    if v:
                        m = re.search(indexation_regexp, v)
                        m_livraison = re.search(indexation_regexp_livraison, v)
                        if m:
                            clef_mercure_livraison = m_livraison.group()[3:]
                            clef_mercure_article = m.group()[3:]
                            try:
                                F2_article_uri = she(cache_corpus.get_uuid(
                                    ["Corpus", "Livraisons", clef_mercure_livraison, "Expression TEI", "Articles",
                                     clef_mercure_article, "F2"]))
                                E13_index_uri = she(
                                    cache_congregations.get_uuid(["congregations", identifier, "indexation", "E13"], True))
                                t(E13_index_uri, a, crm("E13_Attribute_Assignement"))
                                t(E13_index_uri, DCTERMS.created, ro(concept, DCTERMS.created))
                                t(E13_index_uri, crm("P14_carried_out_by"), she("684b4c1a-be76-474c-810e-0f5984b47921"))
                                t(E13_index_uri, crm("P140_assigned_attribute_to"), F2_article_uri)
                                t(E13_index_uri, crm("P141_assigned"), E74_uri)
                                t(E13_index_uri, crm("P177_assigned_property_type"), crm("P67_refers_to"))

                            except:
                                print(identifier, clef_mercure_article)
                                pass

            elif "##" in v:
                v = v.split("##")
                for v in v:
                    if v:
                        m = re.search(indexation_regexp, v)
                        m_livraison = re.search(indexation_regexp_livraison, v)
                        if m:
                            clef_mercure_livraison = m_livraison.group()[3:]
                            clef_mercure_article = m.group()[3:]
                            try:
                                F2_article_uri = she(cache_corpus.get_uuid(
                                    ["Corpus", "Livraisons", clef_mercure_livraison, "Expression TEI", "Articles",
                                     clef_mercure_article, "F2"]))
                                E13_index_uri = she(
                                    cache_congregations.get_uuid(["congregations", identifier, "indexation", "E13"], True))
                                t(E13_index_uri, a, crm("E13_Attribute_Assignement"))
                                t(E13_index_uri, DCTERMS.created, ro(concept, DCTERMS.created))
                                t(E13_index_uri, crm("P14_carried_out_by"), she("684b4c1a-be76-474c-810e-0f5984b47921"))
                                t(E13_index_uri, crm("P140_assigned_attribute_to"), F2_article_uri)
                                t(E13_index_uri, crm("P141_assigned"), E74_uri)
                                t(E13_index_uri, crm("P177_assigned_property_type"), crm("P67_refers_to"))

                            except:
                                print(identifier, clef_mercure_article)
                                pass

            else:
                note_sha1_object = hashlib.sha1(v.encode())
                note_sha1 = note_sha1_object.hexdigest()
                E13_note_uri = she(cache_congregations.get_uuid(["congregations", identifier, "note", "E13"], True))
                t(E13_note_uri, a, crm("E13_Attribute_Assignement"))
                t(E13_note_uri, DCTERMS.created, ro(concept, DCTERMS.created))
                t(E13_note_uri, crm("P14_carried_out_by"), she("684b4c1a-be76-474c-810e-0f5984b47921"))
                t(E13_note_uri, crm("P140_assigned_attribute_to"), E74_uri)
                note_uri = she(cache_congregations.get_uuid(["congregations", identifier, "note", note_sha1], True))
                t(note_uri, RDFS.label, Literal(v))
                t(E13_note_uri, crm("P141_assigned"), note_uri)
                t(E13_note_uri, crm("P177_assigned_property_type"), crm("P3_has_note"))

    for note in [SKOS.note, SKOS.historyNote]:
        process_note(note)

    # NARROWERS
    q = sparql.prepareQuery("""
    SELECT ?narrower ?narrower_prefLabel ?narrower_id
    WHERE {
        ?concept <http://www.w3.org/2004/02/skos/core#narrower> ?narrower .
        ?narrower <http://purl.org/dc/terms/identifier> ?narrower_id .
        ?narrower <http://www.w3.org/2004/02/skos/core#prefLabel> ?narrower_prefLabel .
    }
    ORDER BY ?narrower_prefLabel
    """)

    for row in input_graph.query(q, initBindings={'concept': concept}):

        E74_narrower_uri = she(cache_congregations.get_uuid(["congregations", row[2], "uuid"], True))
        t(E74_uri, crm("P107_has_current_or_former_member"), E74_narrower_uri)

        explore(row[0], depth + 1)

####################################################################################
# GENERATION DU TURTLE
####################################################################################

F34_congregations_uri = URIRef(iremus_ns["a5145217-5642-4f08-8566-1c1bbe9c0b4e"])
t(F34_congregations_uri, a, crm("F34_Controlled_Vocabulary"))
t(F34_congregations_uri, crm("P1_is_identified_by"), Literal("Congrégations religieuses"))

explore(URIRef("https://opentheso3.mom.fr/opentheso3/?idc=clerge_regulier&idt=166"), 0)
t(F34_congregations_uri, she_ns("sheP_a_pour_entité_de_plus_haut_niveau"),
  she(cache_congregations.get_uuid(["congregations", "clerge_regulier", "uuid"], True)))

explore(URIRef("https://opentheso3.mom.fr/opentheso3/?idc=clerge_seculier&idt=166"), 0)
t(F34_congregations_uri, she_ns("sheP_a_pour_entité_de_plus_haut_niveau"),
  she(cache_congregations.get_uuid(["congregations", "clerge_seculier", "uuid"], True)))

explore(URIRef("https://opentheso3.mom.fr/opentheso3/?idc=papaute&idt=166"), 0)
t(F34_congregations_uri, she_ns("sheP_a_pour_entité_de_plus_haut_niveau"),
  she(cache_congregations.get_uuid(["congregations", "papaute", "uuid"], True)))

serialization = output_graph.serialize(format="turtle", base="http://data-iremus.huma-num.fr/id/")
with open(args.output_ttl, "wb") as f:
    f.write(serialization)

cache_congregations.bye()
