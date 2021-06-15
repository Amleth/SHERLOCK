import argparse
from openpyxl import load_workbook
import sys, os
sys.path.append(os.path.abspath(os.path.join('rdfizers/', '')))
# print(sys.path)
from helpers_rdf import *
from helpers_python import *
from sherlockcachemanagement import Cache

######################################################################################
# CACHES
######################################################################################

parser = argparse.ArgumentParser()
parser.add_argument("--xlsx")
parser.add_argument("--ttl")
parser.add_argument("--cache")
parser.add_argument("--cache_corpus")
args = parser.parse_args()

cache = Cache(args.cache)
cache_corpus = Cache(args.cache_corpus)

######################################################################################
# INITIALISATION DU GRAPHE
######################################################################################

g = Graph()

crm_ns = Namespace("http://www.cidoc-crm.org/cidoc-crm/")
crmdig_ns = Namespace("http://www.ics.forth.gr/isl/CRMdig/")
iremus_ns = Namespace("http://data-iremus.huma-num.fr/id/")
lrmoo_ns = Namespace("http://www.cidoc-crm.org/lrmoo/")
sdt_ns = Namespace("http://data-iremus.huma-num.fr/datatypes/")
sherlock_ns = Namespace("http://data-iremus.huma-num.fr/ns/sherlock#")

g.bind("crm", crm_ns)
g.bind("dcterms", DCTERMS)
g.bind("lrm", lrmoo_ns)
g.bind("sdt", sdt_ns)
g.bind("skos", SKOS)
g.bind("crmdig", crmdig_ns)
g.bind("she_ns", sherlock_ns)
g.bind("she", iremus_ns)

######################################################################################
# FONCTIONS RDF
######################################################################################

a = RDF.type

def crm(x):
    return crm_ns[x]

def crmdig(x):
    return crmdig_ns[x]

def lrm(x):
    return lrmoo_ns[x]

def she(x):
    return iremus_ns[x]

def she_ns(x):
    return sherlock_ns[x]

def t(s, p, o):
    g.add((s, p, o))


#######################################################################################
# RECUPERATION DES DONNEES
#######################################################################################

# Fichier Excel
sheet = load_workbook(args.xlsx).active

for row in sheet.iter_rows(min_row=2):

    if row[5].value:
        id = row[5].value.replace(" ", "_").lower()
    else:
        id = (row[2].value + row[4].value).lower().replace(" ", "_").replace(",", "_")

    # Oeuvre musicale (F1 et F2)
    F1_oeuvre_uuid = she(cache.get_uuid([id, "oeuvre musicale", "F1", "uuid"], True))
    t(F1_oeuvre_uuid, a, lrm("F1_Work"))
    F2_oeuvre_uuid = she(cache.get_uuid([id, "oeuvre musicale", "F2", "uuid"], True))
    t(F2_oeuvre_uuid, a, lrm("F2_Expression"))
    t(F1_oeuvre_uuid, lrm("R3_is_realised_in"), F2_oeuvre_uuid)
    F1_oeuvre_uuid_E42_catalogues = she(cache.get_uuid([id, "oeuvre musicale", "F1", "E42 catalogues", "uuid"], True))
    t(F1_oeuvre_uuid, crm("P1_is_identified_by"), F1_oeuvre_uuid_E42_catalogues)
    t(F1_oeuvre_uuid_E42_catalogues, a, crm("E42_Identifier"))
    if row[52].value:
        t(F1_oeuvre_uuid_E42_catalogues, RDFS.label, l(row[52].value))
    F1_oeuvre_uuid_E42_Philidor = she(cache.get_uuid([id, "oeuvre musicale", "F1", "E42 Philidor", "uuid"], True))
    t(F1_oeuvre_uuid, crm("P1_is_identified_by"), F1_oeuvre_uuid_E42_Philidor)
    t(F1_oeuvre_uuid_E42_Philidor, a, crm("E42_Identifier"))
    t(F1_oeuvre_uuid_E42_Philidor, RDFS.label, l(row[13].value))

    # Incipit de l'oeuvre musicale
    if row[5].value:
        F1_oeuvre_appellation = she(cache.get_uuid([id, "oeuvre musicale", "F1", "E41", "uuid"], True))
        t(F1_oeuvre_appellation, a, crm("E41_Appellation"))
        t(F1_oeuvre_appellation, a, crm("E33_Linguistic_Object"))
        t(F1_oeuvre_uuid, crm("P1_is_identified_by"), F1_oeuvre_appellation)

        ## E13 : l'appellation est de type "incipit"
        F1_oeuvre_appellation_E13 = she(cache.get_uuid([id, "oeuvre musicale", "F1", "E41", "E13", "type incipit"], True))
        t(F1_oeuvre_appellation_E13, a, crm("E13_Attribute_Assignement"))
        t(F1_oeuvre_appellation_E13, crm("P14_carried_out_by"), she("684b4c1a-be76-474c-810e-0f5984b47921"))
        t(F1_oeuvre_appellation_E13, crm("P140_assigned_attribute_to"), F1_oeuvre_appellation)
        t(F1_oeuvre_appellation_E13, crm("P141_assigned"), she("e43ce57c-8bf7-43b5-87a2-cf8c140030a6"))
        t(F1_oeuvre_appellation_E13, crm("P177_assigned_property_type"), crm("P2_has_type"))

        ## E13 : l'appellation a pour contenu symbolique...
        F1_oeuvre_appellation_P190_E13 = she(cache.get_uuid([id, "oeuvre musicale", "F1", "E41", "E13", "P190"], True))
        t(F1_oeuvre_appellation_P190_E13, a, crm("E13_Attribute_Assignement"))
        t(F1_oeuvre_appellation_P190_E13, crm("P14_carried_out_by"), she("684b4c1a-be76-474c-810e-0f5984b47921"))
        t(F1_oeuvre_appellation_P190_E13, crm("P140_assigned_attribute_to"), F1_oeuvre_appellation)
        t(F1_oeuvre_appellation_P190_E13, crm("P141_assigned"), l(row[5].value))
        t(F1_oeuvre_appellation_P190_E13, crm("P177_assigned_property_type"), crm("P190_has_symbolic_content"))

        ## E13 : code de l'incipit
        F1_oeuvre_appellation_P1_E13 = she(cache.get_uuid([id, "oeuvre musicale", "F1", "E41", "E13", "code incipit"], True))
        t(F1_oeuvre_appellation_P1_E13, a, crm("E13_Attribute_Assignement"))
        t(F1_oeuvre_appellation_P1_E13, crm("P14_carried_out_by"), she("684b4c1a-be76-474c-810e-0f5984b47921"))
        t(F1_oeuvre_appellation_P1_E13, crm("P140_assigned_attribute_to"), F1_oeuvre_appellation)
        t(F1_oeuvre_appellation_P1_E13, crm("P141_assigned"), l(row[39].value))
        t(F1_oeuvre_appellation_P1_E13, crm("P177_assigned_property_type"), crm("P190_has_symbolic_content"))

    # L'oeuvre musicale et composée d'un texte
    F1_texte_uuid = she(cache.get_uuid([id, "texte", "F1", "uuid"], True))
    t(F1_texte_uuid, a, lrm("F1_Work"))
    F2_texte_uuid = she(cache.get_uuid([id, "texte", "F2", "uuid"], True))
    t(F2_texte_uuid, a, lrm("F2_Expression"))
    t(F1_texte_uuid, lrm("R3_is_realised_in"), F2_texte_uuid)
    t(F1_oeuvre_uuid, lrm("R10_has_member"), F1_texte_uuid)
    t(F2_oeuvre_uuid, crm("P165_incorporates"), F2_texte_uuid)

    # L'oeuvre musicale et composée d'un air
    F1_air_uuid = she(cache.get_uuid([id, "air", "F1", "uuid"], True))
    t(F1_air_uuid, a, lrm("F1_Work"))
    F2_air_uuid = she(cache.get_uuid([id, "air", "F2", "uuid"], True))
    t(F2_air_uuid, a, lrm("F2_Expression"))
    t(F1_air_uuid, lrm("R3_is_realised_in"), F2_air_uuid)
    t(F1_oeuvre_uuid, lrm("R10_has_member"), F1_air_uuid)
    t(F2_oeuvre_uuid, crm("P165_incorporates"), F2_air_uuid)

    # Rattachement de l'oeuvre musicale à son article
    # TODO cellules multivaluées
    indexation_articles = row[15].value.split("\t")
    for article in indexation_articles:
        id_article = article.lstrip("Mercure Galant/ ").replace(", p. ", "_")
        id_article = id_article.split("-")
        id_article = id_article[0].replace(".", "-")
    id_livraison = id_article.split("_")
    id_livraison = id_livraison[0]

    # try:
    #     ## Livraison originale
    #     ### Air
    #     livraison_F2_originale = she(
    #         cache_corpus.get_uuid(["Corpus", "Livraisons", id_livraison, "Expression originale", "F2"]))
    #     t(livraison_F2_originale, crm("P148_has_component"), F2_air_uuid)
    #     ### Texte
    #     livraison_F2_originale = she(
    #         cache_corpus.get_uuid(["Corpus", "Livraisons", id_livraison, "Expression originale", "F2"]))
    #     t(livraison_F2_originale, crm("P148_has_component"), F2_texte_uuid)
    #     ### Livraison TEI
    #     ## Air
    #     livraison_F2_TEI = she(
    #         cache_corpus.get_uuid(["Corpus", "Livraisons", id_livraison, "Expression TEI", "F2"]))
    #     t(livraison_F2_TEI, crm("P148_has_component"), F2_air_uuid)
    #     ## Texte
    #     livraison_F2_TEI = she(
    #         cache_corpus.get_uuid(["Corpus", "Livraisons", id_livraison, "Expression TEI", "F2"]))
    #     t(livraison_F2_TEI, crm("P148_has_component"), F2_texte_uuid)
    # except:
    #     print("L'article ou la livraison", id_article, "(" + id_livraison + ") est introuvable")

    # Note sur la musique
    F2_air_note_E13 = she(cache.get_uuid([id, "air", "F2", "note sur la musique"], True))
    t(F2_air_note_E13, a, crm("E13_Attribute_Assignement"))
    t(F2_air_note_E13, crm("P14_carried_out_by"), she("684b4c1a-be76-474c-810e-0f5984b47921"))
    t(F2_air_note_E13, crm("P140_assigned_attribute_to"), F2_air_uuid)
    t(F2_air_note_E13, crm("P141_assigned"), l(row[26].value))
    t(F2_air_note_E13, crm("P177_assigned_property_type"), she("768197b9-6cc6-4a62-aec9-7282a9c07983"))

    # Genre musical de l'air
    F2_air_genre_E13 = she(cache.get_uuid([id, "air", "F2", "genre musical"], True))
    t(F2_air_genre_E13, a, crm("E13_Attribute_Assignement"))
    t(F2_air_genre_E13, crm("P14_carried_out_by"), she("684b4c1a-be76-474c-810e-0f5984b47921"))
    t(F2_air_genre_E13, crm("P140_assigned_attribute_to"), F2_air_uuid)
    t(F2_air_genre_E13, crm("P141_assigned"), l(row[33].value))
    t(F2_air_genre_E13, crm("P177_assigned_property_type"), she("e6836743-fa50-4995-b534-ba13d1d24380"))

    # Composition de l'air
    F2_air_F28_uuid = she(cache.get_uuid([id, "air", "F2", "F28", "uuid"], True))
    t(F2_air_F28_uuid, a, lrm("F28_Expression_Creation"))
    t(F2_air_F28_uuid, lrm("R17_created"), F2_air_uuid)

    ## Compositeur
    if row[2].value:
        F2_air_F28_compositeur = she(cache.get_uuid([id, "air", "F2", "F28", "compositeur", "uuid"], True))
        t(F2_air_F28_compositeur, a, crm("E21_Person"))
        F2_air_F28_compositeur_E41 = she(cache.get_uuid([id, "air", "F2", "F28", "compositeur", "E41"], True))
        t(F2_air_F28_compositeur, crm("P1_is_identified_by"), F2_air_F28_compositeur_E41)
        t(F2_air_F28_compositeur_E41, RDFS.label, l(row[2].value))

        ## E13 de rattachement du compositeur à la composition
        F2_air_F28_E13 = she(cache.get_uuid([id, "air", "F2", "F28", "E13"], True))
        t(F2_air_F28_E13, a, crm("E13_Attribute_Assignement"))
        t(F2_air_F28_E13, crm("P14_carried_out_by"), she("684b4c1a-be76-474c-810e-0f5984b47921"))
        t(F2_air_F28_E13, crm("P140_assigned_attribute_to"), F2_air_F28_uuid)
        t(F2_air_F28_E13, crm("P141_assigned"), F2_air_F28_compositeur)
        t(F2_air_F28_E13, crm("P177_assigned_property_type"), crm("P14_carried_out_by"))
        if row[21].value:
            t(F2_air_F28_E13, crm("P3_has_note"), l(row[21].value))
        #TODO Aligner le compositeur sur le référentiel des personnes

    # Effectif musical #TODO Rattacher à l'oeuvre ou à l'air?
    F2_air_effectif_musical = she(cache.get_uuid([id, "air", "F2", "effectif musical", "uuid"], True))
    t(F2_air_effectif_musical, a, crm("E55_Type"))
    t(F2_air_effectif_musical, crm("P1_is_identified_by"), l(row[42].value))
    F2_air_effectif_musical_E13 = she(cache.get_uuid([id, "air", "F2", "effectif musical", "E13"], True))
    t(F2_air_effectif_musical_E13, a, crm("E13_Attribute_Assignement"))
    t(F2_air_effectif_musical_E13, crm("P14_carried_out_by"), she("684b4c1a-be76-474c-810e-0f5984b47921"))
    t(F2_air_effectif_musical_E13, crm("P140_assigned_attribute_to"), F2_air_uuid)
    t(F2_air_effectif_musical_E13, crm("P141_assigned"), F2_air_effectif_musical)
    t(F2_air_effectif_musical_E13, crm("P177_assigned_property_type"), crm("P2_has_type"))

    # Instrument mentionné
    if row[43].value:
        F2_air_instrument_E13 = she(cache.get_uuid([id, "air", "F2", "instrument", "E13"], True))
        t(F2_air_instrument_E13, a, crm("E13_Attribute_Assignement"))
        t(F2_air_instrument_E13, crm("P14_carried_out_by"), she("684b4c1a-be76-474c-810e-0f5984b47921"))
        t(F2_air_instrument_E13, crm("P140_assigned_attribute_to"), F2_air_uuid)
        t(F2_air_instrument_E13, crm("P141_assigned"), l(row[43].value))
        t(F2_air_instrument_E13, crm("P177_assigned_property_type"), she("46561c75-fc5d-4f0c-9b82-ea8779264bfd"))

    # Ecriture du texte
    F2_texte_F28_uuid = she(cache.get_uuid([id, "texte", "F2", "F28", "uuid"], True))
    t(F2_texte_F28_uuid, a, lrm("F28_Expression_Creation"))
    t(F2_texte_F28_uuid, lrm("R17_created"), F2_texte_uuid)

    ## Auteur-e
    if row[18].value:
        F2_texte_F28_auteur = she(cache.get_uuid([id, "texte", "F2", "F28", "auteur", "uuid"], True))
        t(F2_texte_F28_auteur, a, crm("E21_Person"))
        F2_texte_F28_auteur_E41 = she(cache.get_uuid([id, "texte", "F2", "F28", "auteur", "E41"], True))
        t(F2_texte_F28_auteur, crm("P1_is_identified_by"), F2_texte_F28_auteur_E41)
        t(F2_texte_F28_auteur_E41, RDFS.label, l(row[18].value))

        ## E13 de rattachement de l'auteur-e du texte
        F2_texte_F28_E13 = she(cache.get_uuid([id, "texte", "F2", "F28", "E13"], True))
        t(F2_texte_F28_E13, a, crm("E13_Attribute_Assignement"))
        t(F2_texte_F28_E13, crm("P14_carried_out_by"), she("684b4c1a-be76-474c-810e-0f5984b47921"))
        t(F2_texte_F28_E13, crm("P140_assigned_attribute_to"), F2_texte_F28_uuid)
        t(F2_texte_F28_E13, crm("P141_assigned"), F2_texte_F28_auteur)
        t(F2_texte_F28_E13, crm("P177_assigned_property_type"), crm("P14_carried_out_by"))
        #TODO Aligner le compositeur sur le référentiel des personnes

    # TODO Alignement du texte aux référentiels (l. 41 de la modélisation)
    # Lieux concernés
    if row[9].value:
        lieux = row[9].value.split("\t")
        for lieu in lieux:
            F2_texte_lieu_E13 = she(cache.get_uuid([id, "texte", "F2", "lieux concernés", "E13"], True))
            t(F2_texte_lieu_E13, a, crm("E13_Attribute_Assignement"))
            t(F2_texte_lieu_E13, crm("P14_carried_out_by"), she("684b4c1a-be76-474c-810e-0f5984b47921"))
            t(F2_texte_lieu_E13, crm("P140_assigned_attribute_to"), F2_texte_uuid)
            t(F2_texte_lieu_E13, crm("P141_assigned"), l(lieu))
            t(F2_texte_lieu_E13, crm("P177_assigned_property_type"), crm("P67_refers_to"))
            #TODO Alignement au référentiel des lieux : comment faire à partir du nom de lieu et non de son id?

    # TODO Colonne H "Note sur les dates" : quelles dates? Ajouter simplement un P3(E13) sur le F2 de l'air?



#######################################################################################
# CREATION DU GRAPHE ET DU CACHE
#######################################################################################

cache.bye()

serialization = g.serialize(format="turtle", base="http://data-iremus.huma-num.fr/id/")
with open(args.ttl, "wb") as f:
    f.write(serialization)

