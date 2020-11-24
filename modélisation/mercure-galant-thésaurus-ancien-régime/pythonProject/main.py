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
    livraison_originale_E52_uri = URIRef(iremus_ns[str(uuid.uuid4())])
    g.add((livraison_originale_E52_uri, RDF.type, URIRef(crm_ns["E52_Time-Span"])))
    livraison_originale_date_uri = root.xpath('string(//tei:creation/tei:date/@when)', namespaces=tei_ns)
    g.add((livraison_originale_E52_uri, URIRef(crm_ns["P80_end_is_qualified_by"]), Literal(livraison_originale_date_uri)))
    g.add((livraison_F2_originale_E63_uri, URIRef(crm_ns["P4_has-time"]), livraison_originale_E52_uri))
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
    g.add((livraison_D2_uri, URIRef(crm_ns["had_output"]), livraison_D1_uri))
    g.add((livraison_D1_uri, RDF.type, URIRef(crmdig_ns["D1_Digital_Object"])))
    g.add((livraison_D1_uri, RDF.type, URIRef(crm_ns["F2_Expression"])))
    livraison_D1_E42_uri = URIRef(iremus_ns[str(uuid.uuid4())])
    g.add((livraison_D1_E42_uri, RDF.type, URIRef(crm_ns["E42_Identifier"])))
    g.add((livraison_D1_uri, URIRef(crm_ns["P1_is_identified_by"]), livraison_D1_E42_uri))
    g.add((livraison_D1_E42_uri, URIRef(crm_ns["P2_has_type"]), URIRef(iremus_ns["f4262bac-f72c-40e2-aa51-ae352da5a35c"])))
    g.add((livraison_D1_E42_uri, RDFS.label,
           ))


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

    ################################################################################
    # ARTICLES
    ################################################################################


'''
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

'''

turtle = g.serialize(format="turtle", base="http://data-iremus.huma-num.fr/id/").decode("utf-8")
print(turtle)


