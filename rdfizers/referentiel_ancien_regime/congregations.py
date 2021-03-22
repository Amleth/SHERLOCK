import argparse
from rdflib.plugins import sparql
from rdflib import Graph, Literal, Namespace, DCTERMS, RDF, RDFS, SKOS, URIRef, URIRef as u, Literal as l
import xlsxwriter
import uuid
import yaml
from sherlockcachemanagement import Cache
import re
import hashlib

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

##################################################################################
## INITIALISATION DES GRAPHES
##################################################################################

input_graph = Graph()
input_graph.load(args.input_rdf)

output_graph = Graph()

crm_ns = Namespace("http://www.cidoc-crm.org/cidoc-crm/")
iremus_ns = Namespace("http://data-iremus.huma-num.fr/id/")
lrmoo_ns = Namespace("http://www.cidoc-crm.org/lrmoo/")
sdt_ns = Namespace("http://data-iremus.huma-num.fr/datatypes/")

output_graph.bind("crm", crm_ns)
output_graph.bind("dcterms", DCTERMS)
output_graph.bind("lrmoo", lrmoo_ns)
output_graph.bind("sdt", sdt_ns)
output_graph.bind("skos", SKOS)

a = RDF.type


##################################################################################
## FONCTIONS
##################################################################################

def crm(x):
    return URIRef(crm_ns[x])


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


def count_concepts():
    q = g.query(
        """
        SELECT (COUNT(?concept) AS ?n)
        WHERE {
            ?concept <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://www.w3.org/2004/02/skos/core#Concept> .
        }
        """)
    return int(list(q)[0][0])

#print(f"{count_concepts()} concepts à traiter")

def explore(concept, depth):

    concept_id = ro(concept, DCTERMS.identifier)
    E74_uri = she(cache_congregations.get_uuid(["congregations", concept_id, "uuid"], True))
    t(E32_ancien_regime_uri, crm("P71_lists"), E74_uri)
    t(E32_congregations_uri, crm("P71_lists"), E74_uri)


    # APPELLATION

    E41_uri = she(cache_congregations.get_uuid(["congregations", concept_id, "E41"], True))
    t(E74_uri, crm("P1_is_identified_by"), E41_uri)
    t(E41_uri, a, crm("E41_Appellation"))
    for prefLabel in ro_list(concept, SKOS.prefLabel):
        t(E41_uri, RDFS.label, prefLabel)

    altLabels = ro_list(concept, SKOS.altLabel)
    if len(altLabels) > 0:
        for altLabel in altLabels:
            E41_alt_uri = she(cache_congregations.get_uuid(["congregations", concept_id, "E41_alt", altLabel], True))
            t(E41_alt_uri, a, crm("E41_Appellation"))
            t(E41_alt_uri, RDFS.label, altLabel)
            t(E41_uri, crm("P139_has_alternative_form"), E41_alt_uri)


    #ALIGNEMENT AU REFERENTIEL DES LIEUX - SOUCI D'ENCODAGE?

    """
    with open(args.situation_geo, "r") as txt:
        texte = txt.read()
        recherche_id = re.search(f"{concept_id}\s", texte)
        if recherche_id :
            for prefLabel in ro_list(concept, SKOS.prefLabel):
                label = prefLabel.lower()
                with open(args.cache_lieux_uuid, "r") as file:
                    input_yaml_parse = yaml.load(file, Loader=yaml.FullLoader)
                    for cle in input_yaml_parse.keys():
                        try:
                            recherche_lieu = re.search(f"{cle}\s", label)
                            if recherche_lieu:
                                print("SUCCES", cle, "   ", label)
                                # t(lieu_uuid, she("sheP_situation_géohistorique"), E74_uri)

                            #A REPRENDRE
                            #else:
                             #   print(label, " --> lieu introuvable")


                        except:
                            print("ERREUR", cle)
    """


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
                            clef_mercure_livraison = m_livraison.group()
                            clef_mercure_article = m.group()
                            try:
                                F2_article_uri = she(cache_corpus.get_uuid(
                                    ["Corpus", "Livraisons", clef_mercure_livraison, "Expression TEI", "Articles",
                                     clef_mercure_article, "F2"]))
                                E13_index_uri = she(
                                    cache_congregations.get_uuid(["congregations", concept_id, "E13_indexation"], True))
                                t(E13_index_uri, a, crm("E13_Attribute_Assignement"))
                                t(E13_index_uri, DCTERMS.created, ro(concept, DCTERMS.created))
                                t(E13_index_uri, crm("P14_carried_out_by"), she("899e29f6-43d7-4a98-8c39-229bb20d23b2"))
                                t(E13_index_uri, crm("P14_carried_out_by"), she("82476bac-cd8a-4bdc-a695-cf90444c9432"))
                                t(E13_index_uri, crm("P140_assigned_attribute_to"), F2_article_uri)
                                t(E13_index_uri, crm("P141_assigned"), E74_uri)
                                t(E13_index_uri, crm("P177_assigned_property_type"), she("sheP_désigne"))

                            except:
                                # print(identifier, clef_mercure_article)
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
                                F2_article_uri = she(cache_corpus.get_uuid(
                                    ["Corpus", "Livraisons", clef_mercure_livraison, "Expression TEI", "Articles",
                                     clef_mercure_article, "F2"]))
                                E13_index_uri = she(
                                    cache_congregations.get_uuid(["congregations", concept_id, "E13_indexation"], True))
                                t(E13_index_uri, a, crm("E13_Attribute_Assignement"))
                                t(E13_index_uri, DCTERMS.created, ro(concept, DCTERMS.created))
                                t(E13_index_uri, crm("P14_carried_out_by"), she("899e29f6-43d7-4a98-8c39-229bb20d23b2"))
                                t(E13_index_uri, crm("P14_carried_out_by"), she("82476bac-cd8a-4bdc-a695-cf90444c9432"))
                                t(E13_index_uri, crm("P140_assigned_attribute_to"), F2_article_uri)
                                t(E13_index_uri, crm("P141_assigned"), E74_uri)
                                t(E13_index_uri, crm("P177_assigned_property_type"), she("sheP_désigne"))

                            except:
                                # print(identifier, clef_mercure_article)
                                pass

            else:
                note_sha1_object = hashlib.sha1(v.encode())
                note_sha1 = note_sha1_object.hexdigest()
                E13_uri = she(cache_congregations.get_uuid(["congregations", concept_id, "E13_indexation"], True))
                t(E13_uri, a, crm("E13_Attribute_Assignement"))
                t(E13_uri, DCTERMS.created, ro(concept, DCTERMS.created))
                t(E13_uri, crm("P14_carried_out_by"), she("899e29f6-43d7-4a98-8c39-229bb20d23b2"))
                t(E13_uri, crm("P14_carried_out_by"), she("82476bac-cd8a-4bdc-a695-cf90444c9432"))
                t(E13_uri, crm("P140_assigned_attribute_to"), E74_uri)
                E13_notes_uri = she(cache_congregations.get_uuid(["congregations", concept_id, "E13_notes", note_sha1], True))
                t(E13_notes_uri, RDFS.label, Literal(v))
                t(E13_uri, crm("P141_assigned"), E13_notes_uri)
                t(E13_uri, crm("P177_assigned_property_type"), crm("P3_has_note"))

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

E32_ancien_regime_uri = URIRef(iremus_ns["b18e2fad-4827-4533-946a-1b9914df6e18"])
E32_congregations_uri = URIRef(iremus_ns["a5145217-5642-4f08-8566-1c1bbe9c0b4e"])
t(E32_ancien_regime_uri, a, crm("E32_Authority_Document"))
t(E32_ancien_regime_uri, crm("P1_is_identified_by"), Literal("Ancien Régime"))
t(E32_ancien_regime_uri, she("sheP_a_pour_entité_de_plus_haut_niveau"), E32_congregations_uri)
t(E32_congregations_uri, a, crm("E32_Authority_Document"))
t(E32_congregations_uri, crm("P1_is_identified_by"), Literal("Congrégations religieuses"))

explore(URIRef("https://opentheso3.mom.fr/opentheso3/?idc=clerge_regulier&idt=166"), 0)
t(E32_congregations_uri, she("sheP_a_pour_entité_de_plus_haut_niveau"),
  she(cache_congregations.get_uuid(["congregations", "clerge_regulier", "uuid"], True)))

explore(URIRef("https://opentheso3.mom.fr/opentheso3/?idc=clerge_seculier&idt=166"), 0)
t(E32_congregations_uri, she("sheP_a_pour_entité_de_plus_haut_niveau"),
  she(cache_congregations.get_uuid(["congregations", "clerge_seculier", "uuid"], True)))

explore(URIRef("https://opentheso3.mom.fr/opentheso3/?idc=papaute&idt=166"), 0)
t(E32_congregations_uri, she("sheP_a_pour_entité_de_plus_haut_niveau"),
  she(cache_congregations.get_uuid(["congregations", "papaute", "uuid"], True)))

output_graph.serialize(destination=args.output_ttl, format="turtle", base="http://data-iremus.huma-num.fr/id/")
cache_corpus.bye()
cache_congregations.bye()
