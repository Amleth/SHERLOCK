import argparse
from lxml import etree
import os
from rdflib import Graph, Literal, Namespace, RDF, RDFS, URIRef
import pathlib
import re
import uuid
import sys
import yaml
from pathlib import Path, PurePath
from sherlockcachemanagement import Cache

parser = argparse.ArgumentParser()
parser.add_argument("--tei")
parser.add_argument("--output_ttl")
parser.add_argument("--corpus_cache")
args = parser.parse_args()  # Où sont stockés tous les paramètres passés en ligne de commande

# CACHE

corpus_cache = Cache(args.corpus_cache)

################################################################################
# Initialisation du graph
################################################################################

g = Graph()

# Namespaces pour préfixage
sdt_ns = Namespace("http://data-iremus.huma-num.fr/datatypes/")
g.bind("sdt", sdt_ns)
crm_ns = Namespace("http://www.cidoc-crm.org/cidoc-crm/")
g.bind("crm", crm_ns)
crmdig_ns = Namespace("http://www.ics.forth.gr/isl/CRMdig/")
g.bind("crmdig", crmdig_ns)
lrmoo_ns = Namespace("http://www.cidoc-crm.org/lrmoo/")
g.bind("lrmoo", lrmoo_ns)

# Helpers
iremus_ns = Namespace("http://data-iremus.huma-num.fr/id/")


def she(x):
    return URIRef(iremus_ns[x])


################################################################################
# DONNEES STATIQUES
################################################################################

# Serial Work
F18 = she(corpus_cache.get_uuid(["Corpus", "F18", "uuid"], True))
g.add((F18, RDF.type, lrmoo_ns["F18_Serial_Work"]))
g.add((F18, crm_ns["P1_is_identified_by"], Literal("Mercure Galant")))
## Work Conception du Serial Work
F27_F18 = she(corpus_cache.get_uuid(["Corpus", "F18", "F27"], True))
g.add((F27_F18, RDF.type, lrmoo_ns["F27_Work_Conception"]))
g.add((F27_F18, lrmoo_ns["R16_initiated"], F18))

# Personnes
Donneau_de_vise = URIRef(iremus_ns["0520c87e-8f8c-4bbf-b205-4631242a8cd6"])
g.add((Donneau_de_vise, RDF.type, crm_ns["E21_Person"]))
g.add((F27_F18, crm_ns["P14_carried_out_by"], Donneau_de_vise))
g.add((Donneau_de_vise, crm_ns["P1_is_identified_by"], Literal("Jean Donneau de Visé")))

tei_ns = {'tei': 'http://www.tei-c.org/ns/1.0'}

for file in os.listdir(args.tei):
    if pathlib.Path(file).suffix != ".xml":
        continue

    try:
        tree = etree.parse(os.path.join(args.tei, file))
    except:
        print("Fichier pourri :", file)
        continue

    root = tree.getroot()

    ################################################################################
    # LIVRAISON
    ################################################################################

    # Work
    livraison_id = file[0:-4]
    livraison_titre = root.xpath('//tei:titleStmt/tei:title/text()', namespaces=tei_ns)[0]
    livraison_F1 = she(corpus_cache.get_uuid(["Corpus", "Livraisons", livraison_id, "F1"], True))
    g.add((F18, URIRef(lrmoo_ns["R10_has_member"]), livraison_F1))
    g.add((livraison_F1, RDF.type, URIRef(lrmoo_ns["F1_Work"])))
    g.add((livraison_F1, URIRef(crm_ns["P1_is_identified_by"]), Literal(livraison_titre)))

    # Expression originale
    livraison_F2_originale = she(
        corpus_cache.get_uuid(["Corpus", "Livraisons", livraison_id, "Expression originale", "F2"], True))
    g.add((livraison_F1, URIRef(lrmoo_ns["R3_is_realised_in"]), livraison_F2_originale))
    g.add((livraison_F2_originale, RDF.type, URIRef(lrmoo_ns["F2_Expression"])))
    # Type = "édition physique"
    g.add((livraison_F2_originale, URIRef(crm_ns["P2_has_type"]),
           URIRef(iremus_ns["7d7fc017-61ba-4f80-88e1-744f1d00dd60"])))
    # Type = "livraison"
    g.add((livraison_F2_originale, URIRef(crm_ns["P2_has_type"]),
           URIRef(iremus_ns["901c2bb5-549d-47e9-bd91-7a21d7cbe49f"])))

    # Manifestation
    livraison_F3 = she(
        corpus_cache.get_uuid(["Corpus", "Livraisons", livraison_id, "Expression originale", "F3"], True))
    g.add((livraison_F3, RDF.type, URIRef(lrmoo_ns["F3_Manifestation"])))
    g.add((livraison_F3, URIRef(lrmoo_ns["R4_embodies"]), livraison_F2_originale))
    # Date de publication
    livraison_F3_F30 = she(
        corpus_cache.get_uuid(["Corpus", "Livraisons", livraison_id, "Expression originale", "F3_F30"], True))
    g.add((livraison_F3_F30, RDF.type, URIRef(crm_ns["F30_Manifestation_Creation"])))
    g.add((livraison_F3_F30, URIRef(lrmoo_ns["R24_created"]), livraison_F3))
    livraison_F3_E52 = she(
        corpus_cache.get_uuid(["Corpus", "Livraisons", livraison_id, "Expression originale", "F3_E52"], True))
    g.add((livraison_F3_E52, RDF.type, URIRef(crm_ns["E52_Time-Span"])))
    livraison_F3_date = root.xpath('string(//tei:creation/tei:date/@when)', namespaces=tei_ns)
    g.add((livraison_F3_E52, URIRef(crm_ns["P82b_end_of_the_end"]), Literal(livraison_F3_date)))
    g.add((livraison_F3_F30, URIRef(crm_ns["P4_has_time-span"]), livraison_F3_E52))

    # Item
    livraison_F5 = she(
        corpus_cache.get_uuid(["Corpus", "Livraisons", livraison_id, "Expression originale", "F5"], True))
    g.add((livraison_F5, RDF.type, URIRef(lrmoo_ns["F5_Item"])))
    g.add((livraison_F5, URIRef(lrmoo_ns["R7_is_materialization_of"]), livraison_F3))
    # Facsimile
    livraison_D2 = she(corpus_cache.get_uuid(["Corpus", "Livraisons", livraison_id, "Facsimile", "D2"], True))
    g.add((livraison_D2, RDF.type, URIRef(crmdig_ns["D2_Digitization_Process"])))
    g.add((livraison_D2, URIRef(crmdig_ns["L1_digitized"]), livraison_F5))
    livraison_D1 = she(corpus_cache.get_uuid(["Corpus", "Livraisons", livraison_id, "Facsimile", "D1"], True))
    g.add((livraison_D1, URIRef(crm_ns["P2_has_type"]), URIRef(iremus_ns["e73699b0-9638-4a9a-bfdd-ed1715416f02"])))
    g.add((livraison_D2, URIRef(crmdig_ns["L11_had_output"]), livraison_D1))
    g.add((livraison_D1, RDF.type, URIRef(crmdig_ns["D1_Digital_Object"])))
    g.add((livraison_D1, URIRef(crm_ns["P130_shows_features_of"]), livraison_F2_originale))

    # Expression TEI
    livraison_F2_tei = she(corpus_cache.get_uuid(["Corpus", "Livraisons", livraison_id, "Expression TEI", "F2"], True))
    g.add((livraison_F1, URIRef(lrmoo_ns["R3_is_realised_in"]), livraison_F2_tei))
    g.add((livraison_F2_tei, RDF.type, URIRef(lrmoo_ns["F2_Expression"])))
    g.add((livraison_F2_tei, RDF.type, URIRef(crmdig_ns["D1_Digital_Object"])))
    g.add((livraison_F2_tei, RDF.type, URIRef(crm_ns["E31_Document"])))

    # URL du fichier TEI
    livraison_F2_tei_E42 = she(
        corpus_cache.get_uuid(["Corpus", "Livraisons", livraison_id, "Expression TEI", "F2_E42"], True))
    g.add((livraison_F2_tei, URIRef(crm_ns["P1_is_identified_by"]), livraison_F2_tei_E42))
    g.add((livraison_F2_tei_E42, RDF.type, URIRef(crm_ns["E42_Identifier"])))
    g.add((livraison_F2_tei_E42, URIRef(crm_ns["P2_has_type"]),
           URIRef(iremus_ns["219fd53d-cdf2-4174-8d71-6d12bdd24016"])))
    g.add((livraison_F2_tei_E42, RDFS.label,
           URIRef(f"http://data-iremus.huma-num.fr/files/mercure-galant/tei/livraisons/MG-{file[3:-4]}.xml")))

    # Identifiant de la TEI
    livraison_F2_tei_E42_id = she(
        corpus_cache.get_uuid(["Corpus", "Livraisons", livraison_id, "Expression TEI", "F2_E42_id"], True))
    g.add((livraison_F2_tei, URIRef(crm_ns["P1_is_identified_by"]), livraison_F2_tei_E42_id))
    g.add((livraison_F2_tei_E42_id, RDF.type, URIRef(crm_ns["E42_Identifier"])))
    g.add((livraison_F2_tei_E42_id, URIRef(crm_ns["P2_has_type"]),
           URIRef(iremus_ns["92c258a0-1e34-437f-9686-e24322b95305"])))
    g.add((livraison_F2_tei_E42_id, RDFS.label, Literal(livraison_id)))

    # Creation de l'expression TEI
    livraison_F2_tei_E65 = she(
        corpus_cache.get_uuid(["Corpus", "Livraisons", livraison_id, "Expression TEI", "F2_E65"], True))
    g.add((livraison_F2_tei_E65, RDF.type, URIRef(crm_ns["E65_Creation"])))
    g.add((livraison_F2_tei_E65, URIRef(crm_ns["P94_has_created"]), livraison_F2_tei))
    g.add((livraison_F2_tei_E65, URIRef(crm_ns["P14_carried_out_by"]),
           URIRef(iremus_ns["684b4c1a-be76-474c-810e-0f5984b47921"])))

    ################################################################################
    # ARTICLES
    ################################################################################

    div = root.xpath('//tei:body//tei:div[@type="article"]', namespaces=tei_ns)
    for article in div:

        # Work
        article_titre_xpath = article.xpath('./tei:head/child::node()', namespaces=tei_ns)
        article_id = article.attrib['{http://www.w3.org/XML/1998/namespace}id']
        article_titre = ""
        for node in article_titre_xpath:
            if type(node) == etree._ElementUnicodeResult:
                article_titre += re.sub(r'\s+', ' ', node.replace("\n", ""))
            if type(node) == etree._Element:
                if node.tag == "{http://www.tei-c.org/ns/1.0}hi":
                    article_titre += re.sub(r'\s+', ' ', node.text.replace("\n", ""))
        article_F1 = she(corpus_cache.get_uuid(
            ["Corpus", "Livraisons", livraison_id, "Expression TEI", "Articles", article_id, "F1"], True))
        g.add((article_F1, RDF.type, URIRef(lrmoo_ns["F1_Work"])))
        g.add((article_F1, URIRef(crm_ns["P1_is_identified_by"]), Literal(article_titre)))
        g.add((livraison_F1, URIRef(lrmoo_ns["R10_has_member"]), article_F1))

        # Expression originale
        article_F2_original = she(corpus_cache.get_uuid(
            ["Corpus", "Livraisons", livraison_id, "Expression originale", "Articles", article_id, "F2"], True))
        g.add((article_F2_original, RDF.type, URIRef(lrmoo_ns["F2_Expression"])))
        ## a pour type "article"
        g.add((article_F2_original, URIRef(crm_ns["P2_has_type"]), URIRef(iremus_ns["13f43e00-680a-4a6d-a223-48e8d9bbeaae"])))
        ## a pour type "édition physique"
        g.add((article_F2_original, URIRef(crm_ns["P2_has_type"]), URIRef(iremus_ns["7d7fc017-61ba-4f80-88e1-744f1d00dd60"])))
        g.add((livraison_F2_originale, URIRef(crm_ns["P148_has_component"]), article_F2_original))
        g.add((article_F1, URIRef(lrmoo_ns["R3_is_realised_in"]), article_F2_original))

        # Expression TEI
        article_F2_tei = she(corpus_cache.get_uuid(
            ["Corpus", "Livraisons", livraison_id, "Expression TEI", "Articles", article_id, "F2"], True))
        g.add((article_F2_tei, RDF.type, URIRef(lrmoo_ns["F2_Expression"])))
        g.add((article_F2_tei, RDF.type, URIRef(crm_ns["E31_Document"])))
        g.add((article_F2_tei, RDF.type, URIRef(crmdig_ns["D1_Digital_Object"])))
        g.add((livraison_F2_tei, URIRef(crm_ns["P148_has_component"]), article_F2_tei))
        g.add((article_F1, URIRef(lrmoo_ns["R3_is_realised_in"]), article_F2_tei))
        ## a pour type "article"
        g.add((article_F2_tei, URIRef(crm_ns["P2_has_type"]), URIRef(iremus_ns["13f43e00-680a-4a6d-a223-48e8d9bbeaae"])))
        ## a pour type "édition TEI"
        g.add((article_F2_tei, URIRef(crm_ns["P2_has_type"]), URIRef(iremus_ns["62b49ca2-ec73-4d72-aaf3-045da6869a15"])))

        ## Identifiant de l'expression TEI
        article_F2_tei_E42 = she(corpus_cache.get_uuid(
            ["Corpus", "Livraisons", livraison_id, "Expression TEI", "Articles", article_id, "F2_E42"], True))
        g.add((article_F2_tei, URIRef(crm_ns["P1_is_identified_by"]), article_F2_tei_E42))
        g.add((article_F2_tei_E42, RDF.type, URIRef(crm_ns["E42_Identifier"])))
        g.add((article_F2_tei_E42, RDFS.label, Literal(article_id)))


serialization = g.serialize(format="turtle", base="http://data-iremus.huma-num.fr/id/")
with open(args.output_ttl, "wb") as f:
    f.write(serialization)
corpus_cache.bye()
