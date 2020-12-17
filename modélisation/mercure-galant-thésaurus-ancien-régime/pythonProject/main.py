import argparse
from lxml import etree
import os
from rdflib import Graph, Literal, Namespace, RDF, RDFS, URIRef
import re
import uuid

parser = argparse.ArgumentParser()
parser.add_argument("--tei")  # Je m'attends à trouver tel argument
parser.add_argument("--ttl")  # Je m'attends à trouver tel argument
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

# Serial Work
F18_uri = URIRef(iremus_ns["4997648d-7ba3-4092-858e-b1c3bebe206b"])
g.add((F18_uri, RDF.type, lrmoo_ns["F18_Serial_Work"]))
g.add((F18_uri, crm_ns["P1_is_identified_by"], Literal("Mercure Galant")))
## Work Conception du Serial Work
F27_F18_uri = URIRef(iremus_ns["d66f5afc-0e6a-41f8-88cb-ed8960634ca8"])
g.add((F27_F18_uri, RDF.type, lrmoo_ns["F27_Work_Conception"]))
g.add((F27_F18_uri, lrmoo_ns["R16_initiated"], F18_uri))

# Personnes
Donneau_de_vise_uri = URIRef(iremus_ns["0520c87e-8f8c-4bbf-b205-4631242a8cd6"])
g.add((Donneau_de_vise_uri, RDF.type, crm_ns["E21_Person"]))
g.add((F27_F18_uri, crm_ns["P14_carried_out_by"], Donneau_de_vise_uri))
g.add((Donneau_de_vise_uri, crm_ns["P1_is_identified_by"], Literal("Jean Donneau de Visé")))


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
    ## Type = "édition physique"
    g.add((livraison_F2_originale_uri, URIRef(lrmoo_ns["P2_has_type"]), URIRef(iremus_ns["7d7fc017-61ba-4f80-88e1-744f1d00dd60"])))
    ## Type = "livraison"
    g.add((livraison_F2_originale_uri, URIRef(lrmoo_ns["P2_has_type"]),
           URIRef(iremus_ns["901c2bb5-549d-47e9-bd91-7a21d7cbe49f"])))

    # Date de l'expression originale
    livraison_F2_originale_E63_uri = URIRef(iremus_ns[str(uuid.uuid4())])
    g.add((livraison_F2_originale_E63_uri, RDF.type, URIRef(crm_ns["E63_Beginning_of_Existence"])))
    livraison_F2_originale_E52_uri = URIRef(iremus_ns[str(uuid.uuid4())])
    g.add((livraison_F2_originale_E52_uri, RDF.type, URIRef(crm_ns["E52_Time-Span"])))
    livraison_F2_originale_date_uri = root.xpath('string(//tei:creation/tei:date/@when)', namespaces=tei_ns)
    g.add((livraison_F2_originale_E52_uri, URIRef(crm_ns["P80_end_is_qualified_by"]), Literal(livraison_F2_originale_date_uri)))
    g.add((livraison_F2_originale_E63_uri, URIRef(crm_ns["P4_has-time"]), livraison_F2_originale_E52_uri))
    g.add((livraison_F2_originale_E63_uri, URIRef(crm_ns["P92_brought_into_existence"]), livraison_F2_originale_uri))

    # Facsimile de l'expression originale
    ## Manifestation
    livraison_F3_uri = URIRef(iremus_ns[str(uuid.uuid4())])
    g.add((livraison_F3_uri, RDF.type, URIRef(crm_ns["F3_Manifestation"])))
    g.add((livraison_F3_uri, URIRef(crm_ns["R4_embodies"]), livraison_F2_originale_uri))
    ## Item
    livraison_F5_uri = URIRef(iremus_ns[str(uuid.uuid4())])
    g.add((livraison_F5_uri, RDF.type, URIRef(crm_ns["F5_Item"])))
    g.add((livraison_F5_uri, URIRef(crm_ns["R7_is_materialization_of"]), livraison_F3_uri))
    ## Facsimile
    livraison_D2_uri = URIRef(iremus_ns[str(uuid.uuid4())])
    g.add((livraison_D2_uri, RDF.type, URIRef(crmdig_ns["D2_Digitization_Process"])))
    g.add((livraison_D2_uri, URIRef(crm_ns["L1_digitized"]), livraison_F5_uri))
    livraison_D1_uri = URIRef(iremus_ns[str(uuid.uuid4())])
    g.add((livraison_D1_uri, URIRef(crm_ns["P2_has_type"]), URIRef(iremus_ns["e73699b0-9638-4a9a-bfdd-ed1715416f02"])))
    g.add((livraison_D2_uri, URIRef(crm_ns["had_output"]), livraison_D1_uri))
    g.add((livraison_D1_uri, RDF.type, URIRef(crmdig_ns["D1_Digital_Object"])))
    g.add((livraison_D1_uri, RDF.type, URIRef(crm_ns["F2_Expression"])))


    # Expression TEI
    livraison_F2_tei_uri = URIRef(iremus_ns[str(uuid.uuid4())])
    g.add((livraison_F1_uri, URIRef(lrmoo_ns["R3_is_realised_in"]), livraison_F2_tei_uri))
    g.add((livraison_F2_tei_uri, RDF.type, URIRef(lrmoo_ns["F2_Expression"])))
    g.add((livraison_F2_tei_uri, RDF.type, URIRef(crmdig_ns["D1_Digital_Object"])))
    g.add((livraison_F2_tei_uri, RDF.type, URIRef(crm_ns["E31_Document"])))
    livraison_F2_tei_E42_uri = URIRef(iremus_ns[str(uuid.uuid4())])
    g.add((livraison_F2_tei_uri, URIRef(crm_ns["P1_is_identified_by"]), livraison_F2_tei_E42_uri))
    g.add((livraison_F2_tei_E42_uri, RDF.type, URIRef(crm_ns["E42_Identifier"])))
    g.add((livraison_F2_tei_E42_uri, URIRef(crmdig_ns["P2_has_type"]),
           URIRef(iremus_ns["219fd53d-cdf2-4174-8d71-6d12bdd24016"])))
    g.add((livraison_F2_tei_E42_uri, RDFS.label,
           URIRef(f"http://data-iremus.huma-num.fr/files/mercure-galant-{file[3:-4]}.tei")))
    ## Creation de l'expression TEI
    livraison_F2_tei_E65_uri = URIRef(iremus_ns[str(uuid.uuid4())])
    g.add((livraison_F2_tei_E65_uri, RDF.type, URIRef(crm_ns["E65_Creation"])))
    g.add((livraison_F2_tei_E65_uri, URIRef(crm_ns["P94_has_created"]), livraison_F2_tei_uri))
    g.add((livraison_F2_tei_E65_uri, URIRef(crm_ns["P14_carried_out_by"]), URIRef(iremus_ns["899e29f6-43d7-4a98-8c39-229bb20d23b2"])))                               ## A MODIFIER?


    ################################################################################
    # ARTICLES
    ################################################################################

    # Work
    div = root.xpath('//tei:body/tei:div[@type="article"]', namespaces=tei_ns)
    for article in div:
        article_F1_uri = URIRef(iremus_ns[str(uuid.uuid4())])
        article_F2_uri = URIRef(iremus_ns[str(uuid.uuid4())])
        g.add((article_F1_uri, RDF.type, URIRef(lrmoo_ns["F1_Work"])))
        g.add((livraison_F1_uri, URIRef(lrmoo_ns["R10_has_member"]), article_F1_uri))
        # Identifiant et titre
        article_titre_xpath = article.xpath('./tei:head/child::node()', namespaces=tei_ns)
        article_id = article.attrib['{http://www.w3.org/XML/1998/namespace}id']
        article_titre = ""
        for node in article_titre_xpath:
            if type(node) == etree._ElementUnicodeResult:
                article_titre += re.sub(r'\s+', ' ', node.replace("\n", ""))
            if type(node) == etree._Element:
                if node.tag == "{http://www.tei-c.org/ns/1.0}hi":
                    article_titre += re.sub(r'\s+', ' ', node.text.replace("\n", ""))
        g.add((article_F1_uri, URIRef(crm_ns["P1_is_identified_by"]), Literal(article_titre)))
        g.add((article_F1_uri, URIRef(lrmoo_ns["R3_is_realised_in"]), article_F2_uri))

        # Expression
        g.add((article_F2_uri, RDF.type, URIRef(lrmoo_ns["F2_Expression"])))
        g.add((article_F2_uri, RDF.type, URIRef(crm_ns["E31_Document"])))
        g.add((article_F2_uri, RDF.type, URIRef(crmdig_ns["D1_Digital_Object"])))
        g.add((article_F2_uri, URIRef(crm_ns["P2_has_type"]),
               URIRef(iremus_ns["62b49ca2-ec73-4d72-aaf3-045da6869a15"])))
        g.add((article_F2_uri, URIRef(crm_ns["P2_has_type"]),
               URIRef(iremus_ns["13f43e00-680a-4a6d-a223-48e8d9bbeaae"])))
        ## Identifiant de l'expression
        article_F2_E42_uri = URIRef(iremus_ns[str(uuid.uuid4())])
        g.add((article_F2_uri, URIRef(crm_ns["P1_is_identified_by"]), article_F2_E42_uri))
        g.add((article_F2_E42_uri, RDF.type, URIRef(crm_ns["E42_Identifier"])))
        g.add((article_F2_E42_uri, URIRef(crm_ns["P2_has_type"]), URIRef(iremus_ns["b486f08e-4d50-4363-97b4-d4ea100818e5"])))
        article_F2_E42_uri_part1 = URIRef(iremus_ns[str(uuid.uuid4())])
        article_F2_E42_uri_part2 = URIRef(iremus_ns[str(uuid.uuid4())])
        ### Parties de l'identifiant
        #### Partie 1
        g.add((article_F2_E42_uri, URIRef(crm_ns["P106_is_composed_of"]), article_F2_E42_uri_part1))
        g.add((article_F2_E42_uri_part1, RDF.type, URIRef(crm_ns["E42_Identifier"])))
        g.add((article_F2_E42_uri_part1, URIRef(crm_ns["P2_has_type"]), URIRef(iremus_ns["9b63d6ef-5c5b-4eca-92f4-76c083918129"])))
        g.add((article_F2_E42_uri_part1, RDFS.label, URIRef(f"http://data-iremus.huma-num.fr/files/mercure-galant-{article_id[3:]}.tei")))
        #### Partie 2
        g.add((article_F2_E42_uri, URIRef(crm_ns["P106_is_composed_of"]), article_F2_E42_uri_part2))
        g.add((article_F2_E42_uri_part2, RDF.type, URIRef(crm_ns["E42_Identifier"])))
        g.add((article_F2_E42_uri_part2, URIRef(crm_ns["P2_has_type"]),
               URIRef(iremus_ns["a1e06dc7-f2d8-403a-8061-50d56411c031"])))
        g.add((article_F2_E42_uri_part2, RDFS.label, Literal("//*[@xml:id='MG-1672-01_000']", datatype="sdt:XPathSelector")))

g.serialize(destination=args.ttl, format="turtle", base="http://data-iremus.huma-num.fr/id/")
