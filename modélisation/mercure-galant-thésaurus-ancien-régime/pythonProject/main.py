import argparse
from lxml import etree
import os
from rdflib import Graph, Literal, Namespace, RDF, RDFS, URIRef
import uuid

parser = argparse.ArgumentParser()
parser.add_argument("--tei")  # Je m'attends à trouver tel argument
args = parser.parse_args()  # Où sont stockés tous les paramètres passés en ligne de commande

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

################################################################################
# Création des données statiques
################################################################################

F18_uri = URIRef(iremus_ns["4997648d-7ba3-4092-858e-b1c3bebe206b"])
g.add((F18_uri, RDF.type, lrmoo_ns["F18_Serial_Work"]))
g.add((F18_uri, crm_ns["p1_is_identified_by"], Literal("Mercure Galant")))

tei_ns = {'tei': 'http://www.tei-c.org/ns/1.0'}

for file in os.listdir(args.tei):
    tree = etree.parse(os.path.join(args.tei, file))
    root = tree.getroot()

    ################################################################################
    # LIVRAISON
    ################################################################################

    # Work
    livraison_F1_uri = URIRef(iremus_ns[str(uuid.uuid4())])
    g.add((F18_uri, URIRef(lrmoo_ns["R10_has_member"]), livraison_F1_uri))
    g.add((livraison_F1_uri, RDF.type, URIRef(lrmoo_ns["F1_Work"])))
    livraison_titre = root.xpath('//tei:titleStmt/tei:title/text()', namespaces=tei_ns)[0]
    g.add((livraison_F1_uri, URIRef(crm_ns["P1_is_identified_by"]), Literal(livraison_titre)))

    # Expression originale
    livraison_F2_originale_uri = URIRef(iremus_ns[str(uuid.uuid4())])
    g.add((livraison_F1_uri, URIRef(lrmoo_ns["R3_is_realised_in"]), livraison_F2_originale_uri))
    g.add((livraison_F2_originale_uri, RDF.type, URIRef(lrmoo_ns["F2_Expression"])))

    # Expression TEI
    livraison_F2_tei_uri = URIRef(iremus_ns[str(uuid.uuid4())])
    g.add((livraison_F1_uri, URIRef(lrmoo_ns["R3_is_realised_in"]), livraison_F2_tei_uri))
    g.add((livraison_F2_tei_uri, RDF.type, URIRef(lrmoo_ns["F2_Expression"])))
    g.add((livraison_F2_tei_uri, RDF.type, URIRef(crmdig_ns["D1_Digital_Object"])))
    g.add((livraison_F2_tei_uri, RDF.type, URIRef(crm_ns["E31_Document"])))
    livraison_F2_tei_identifier_uri = URIRef(iremus_ns[str(uuid.uuid4())])
    g.add((livraison_F2_tei_uri, URIRef(crm_ns["P1_is_identified_by"]), livraison_F2_tei_identifier_uri))
    g.add((livraison_F2_tei_identifier_uri, RDF.type, URIRef(crm_ns["E42_Identifier"])))
    g.add((livraison_F2_tei_identifier_uri, URIRef(crmdig_ns["P2_has_type"]),
           URIRef(iremus_ns["219fd53d-cdf2-4174-8d71-6d12bdd24016"])))
    g.add((livraison_F2_tei_identifier_uri, RDFS.label,
           URIRef(f"http://data-iremus.huma-num.fr/files/mercure-galant-{file[3:-4]}.tei")))

    ################################################################################
    # ARTICLES
    ################################################################################

    for div in root.xpath('//tei:body/tei:div[@type="article"]', namespaces=tei_ns):
        article_id = div.attrib['{http://www.w3.org/XML/1998/namespace}id']
        # TODO prendre head !!!

        bibl = div.find("{http://www.tei-c.org/ns/1.0}bibl")
        bibl_str = ""
        if bibl:
            for node in bibl.xpath("child::node()"):
                if type(node) == etree._ElementUnicodeResult:
                    bibl_str += node
                if type(node) == etree._Element:
                    if node.tag == "{http://www.tei-c.org/ns/1.0}title":
                        bibl_str += node.text
        print(bibl_str)
        #
        #
        #
        # if node.tag == "{http://www.tei-c.org/ns/1.0}title":
        #    print(node.text)

# turtle = g.serialize(format="turtle", base="http://data-iremus.huma-num.fr/id/").decode("utf-8")
# print(turtle)
