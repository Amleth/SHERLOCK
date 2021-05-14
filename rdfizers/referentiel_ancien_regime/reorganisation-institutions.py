# N'ont pas de prefLabel :
#     http://opentheso3.mom.fr/opentheso3/?idc=examinateur_au_ahatelet&idt=173
#     http://opentheso3.mom.fr/opentheso3/?idc=Orchestre_de_la_Comedie_Francaise&idt=173
# Certains concepts sont liés à plusieurs skos:narrower
# Remplacer ' &amp;' par '&amp;'
# Remplacer 'lieutenant_de_police_au_chatelet_(chambre criminelle)' par 'lieutenant_de_police_au_chatelet_(chambre_criminelle)'

import argparse
from pathlib import Path, PurePath
from rdflib.plugins import sparql
from rdflib import (
    Graph,
    Literal,
    Namespace,
    DCTERMS,
    RDF,
    RDFS,
    SKOS,
    URIRef,
    URIRef as u,
    Literal as l,
)
import xlsxwriter

parser = argparse.ArgumentParser()
parser.add_argument("--input_rdf")
parser.add_argument("--thesaurus")
parser.add_argument("--output_xlsx")
args = parser.parse_args()

g = Graph()
g.load(args.input_rdf)

for branche in [
        ["Corporations", "https://opentheso3.mom.fr/opentheso3/?idc=corporation&idt=173"],
        ["Institutions", "https://opentheso3.mom.fr/opentheso3/?idc=institution&idt=173"],
        ["Manufactures", "https://opentheso3.mom.fr/opentheso3/?idc=manufactures&idt=173"]
]:

    if branche[0] != args.thesaurus:
        continue

    workbook = xlsxwriter.Workbook(args.output_xlsx)
    worksheet = workbook.add_worksheet()

    row = -1

    def explore_concept(worksheet, concept, ancestors=[], depth=0):
        global row

        ancestors = ancestors[:]

        # Label
        prefLabels = list(g.objects(concept, SKOS.prefLabel))
        if len(prefLabels) == 0:
            return
        # print("    " * depth, prefLabels[0])
        row += 1
        for i in range(0, depth):
            worksheet.write(row, i, ancestors[i])
            print((row, i, ancestors[i]))
        worksheet.write(row, depth, prefLabels[0])
        #print(row, depth, prefLabels[0])
        ancestors.append(str(prefLabels[0]))

        # Narrowers
        q = sparql.prepareQuery(
            """
            SELECT ?narrower
            WHERE {
                ?concept <http://www.w3.org/2004/02/skos/core#narrower> ?narrower .
                ?narrower <http://www.w3.org/2004/02/skos/core#prefLabel> ?npl .
            }
            ORDER BY ?npl
            """)

        narrowers = list(g.query(q, initBindings={'concept': concept}))
        for narrower in narrowers:
            explore_concept(worksheet, narrower[0], ancestors, depth + 1)

    explore_concept(worksheet, u(branche[1]))

    workbook.close()
