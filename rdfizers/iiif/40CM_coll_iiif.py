# TO DO?
# - Aller chercher les uuid des responsables de collection
# - Créer un cache d'uuid pour les auteurs d'ouvrages et les lier à des E21
# - Dater un F27 : time-span + propriété cidoc ou dcterms:date ?

import xlrd
import argparse
from rdflib import Graph, Literal, Namespace, DCTERMS, RDF, RDFS, SKOS, URIRef, XSD, URIRef as u, Literal as l
import yaml
from sherlockcachemanagement import Cache

# Arguments
parser = argparse.ArgumentParser()
parser.add_argument("--iiif_excel")
parser.add_argument("--output_ttl")
parser.add_argument("--cache_40CM")
args = parser.parse_args()


# Cache
cache_40CM = Cache(args.cache_40CM)


# Initialisation du graphe
output_graph = Graph()


# Namespaces
crm_ns = Namespace("http://www.cidoc-crm.org/cidoc-crm/")
crmdig_ns = Namespace("http://www.ics.forth.gr/isl/CRMdig/")
iremus_ns = Namespace("http://data-iremus.huma-num.fr/id/")
lrmoo_ns = Namespace("http://www.cidoc-crm.org/lrmoo/")
sdt_ns = Namespace("http://data-iremus.huma-num.fr/datatypes/")
she_ns = Namespace("http://data-iremus.huma-num.fr/ns/sherlock#")

output_graph.bind("crm", crm_ns)
output_graph.bind("dcterms", DCTERMS)
output_graph.bind("lrm", lrmoo_ns)
output_graph.bind("sdt", sdt_ns)
output_graph.bind("skos", SKOS)
output_graph.bind("she", she_ns)
output_graph.bind("crmdig", crmdig_ns)


# Fonctions
a = RDF.type

def crm(x):
    return URIRef(crm_ns[x])

def crmdig(x):
    return URIRef(crmdig_ns[x])

def lrm(x):
    return URIRef(lrmoo_ns[x])


def she(x):
    return URIRef(iremus_ns[x])


def t(s, p, o):
    output_graph.add((s, p, o))


# Récupération du fichier excel
with xlrd.open_workbook(args.iiif_excel) as wb:

    #####################################################################
    ## LA COLLECTION
    #####################################################################

    sheet_coll = wb.sheet_by_index(1)
    collection = she(cache_40CM.get_uuid(["collection", "uuid"], True))
    t(collection, a, crmdig("D1_Digital_Object"))
    ### Appellation
    collection_E41 = she(cache_40CM.get_uuid(["collection", "E41"], True))
    t(collection_E41, a, crm("E41_Appellation"))
    t(collection, crm("P1_is_identified_by"), collection_E41)
    t(collection_E41, RDFS.label, Literal(sheet_coll.cell_value(4, 1)))
    t(collection, crm("P2_has_type"), she("14926d58-83e7-4414-90a8-1a3f5ca8fec1"))
    ### Creation
    collection_E65 = she(cache_40CM.get_uuid(["collection", "E65"], True))
    t(collection_E65, a, crm("E65_Creation"))
    t(collection_E65, crm("P94_has_created"), collection)
    t(collection_E65, crm("P14_carried_out_by"), Literal(sheet_coll.cell_value(4, 2))) #Aller chercher l'uuid du-de la responsable
    ### Licence
    collection_E30 = she(cache_40CM.get_uuid(["collection", "E30"], True))
    t(collection_E30, a, crm("E30_Right"))
    t(collection, crm("P104_is_subject_to"), collection_E30)
    t(collection_E30, RDFS.label, Literal(sheet_coll.cell_value(4, 5)))
    ### Attribution
    t(collection, crm("P105_right_held_by"), she("48a8e9ad-4264-4b0b-a76d-953bc9a34498"))


    #####################################################################
    ## LA PUBLICATION
    #####################################################################

    if sheet_coll.cell_value(4, 3) == "Livre":
        ### Work
        livre_F1 = she(cache_40CM.get_uuid(["collection", "livre", "F1"], True))
        t(livre_F1, a, lrm("F1_Work"))
        livre_E41 = she(cache_40CM.get_uuid(["collection", "livre", "E41"], True))
        t(livre_F1, crm("P1_is_identified_by"), livre_E41)
        t(livre_F1, RDFS.label, Literal(sheet_coll.cell_value(4, 6)))
        #### Work Conception
        if sheet_coll.cell_value(4, 7) or sheet_coll.cell_value(4, 9) != None:
            livre_F27 = she(cache_40CM.get_uuid(["collection", "livre", "F27"], True))
            t(livre_F27, a, lrm("F27_Work_Conception"))
            t(livre_F27, lrm("R16_initiated"), livre_F1)
            if sheet_coll.cell_value(4, 7) != None:
                t(livre_F27, crm("P14_carried_out_by"), Literal(sheet_coll.cell_value(4, 7)))
            if sheet_coll.cell_value(4, 9) != None:
                # E52 OU DCTERMS:DATE?
                #livre_E52 = she(cache_40CM.get_uuid(["collection", "livre", "E52"], True))
                #t(livre_F27, crm("P4_has_time-span"), livre_E52)
                #t(livre_E52, DCTERMS.date, Literal(sheet_coll.cell_value(4, 9)))
                t(livre_F27, DCTERMS.date, Literal(sheet_coll.cell_value(4, 9)))

        ### Expression
        livre_F2 = she(cache_40CM.get_uuid(["collection", "livre", "F2"], True))
        t(livre_F1, lrm("R3_is_realised_in"), livre_F2)
        t(livre_F2, a, lrm("F2_Expression"))
        #### Expression Creation
        if sheet_coll.cell_value(4, 8) or sheet_coll.cell_value(4, 10) != None:
            livre_F28 = she(cache_40CM.get_uuid(["collection", "livre", "F28"], True))
            t(livre_F28, a, lrm("F28_Expression_Creation"))
            t(livre_F28, lrm("R17_created"), livre_F2)
            if sheet_coll.cell_value(4, 8) != None:
                t(livre_F28, lrm("P14_carried_out_by"), Literal(sheet_coll.cell_value(4, 8)))
            if sheet_coll.cell_value(4, 10) != None:
                t(livre_F28, DCTERMS.date, Literal(sheet_coll.cell_value(4, 10)))

    #####################################################################
    ## LES IMAGES DE LA COLLECTION
    #####################################################################

    sheet_img = wb.sheet_by_index(0)

    def id_img(row, column):
        id = sheet_img.cell_value(row, column)
        try:
            img_E90 = she(cache_40CM.get_uuid(["collection", "livre", id, "E90"], True))
            t(img_E90, a, crm("E90_Symbolic_Object"))
            img_E42 = she(cache_40CM.get_uuid(["collection", "livre", id, "E42"], True))
            t(img_E42, crm("P2_has_type"), she("466bb717-b90f-4104-8f4e-5a13fdde3bc3"))
            t(img_E90, crm("P1_is_identified_by"), img_E42)
            t(img_E42, RDFS.label, Literal(sheet_img.cell_value(row, column), datatype=XSD.integer))
            id_img(row + 1, column)
        except:
            pass

    id_img(4, 2)


    # Ajouter une condition pour les différents types d'images (page de livre, peinture, gravure) et en faire des E22

    #t(livre_F2, lrm("R15_has_fragment")) une page

    #t(collection, crm("P106_is_composed_of"), UUID DU D1)

output_graph.serialize(destination=args.output_ttl, format="turtle", base="http://data-iremus.huma-num.fr/id/")
cache_40CM.bye()

