import argparse
from rdflib import Literal as l, RDF
from pprint import pprint

from helpers_python import get_xlsx_rows_as_dicts
from helpers_rdf import a, crm, crmdig, init_graph, save_graph, she, t
from sherlockcachemanagement import Cache

parser = argparse.ArgumentParser()
parser.add_argument("--cache")
parser.add_argument("--ttl")
parser.add_argument("--xlsx")
args = parser.parse_args()


init_graph()
cache = Cache(args.cache)


def make_collection(data):
    collection = she(data["uuid"])
    t(collection, a, crmdig("D1_Digital_Object"))
    t(collection, crm("P1_is_identified_by"), l(data["libellé"]))
    t(collection, crm("P2_has_type"), she("14926d58-83e7-4414-90a8-1a3f5ca8fec1"))

    # Création
    E65 = she(cache.get_uuid([data["uuid"], "E65"], True))
    t(E65, a, crm("E65_Creation"))
    t(E65, crm("P94_has_created"), collection)
    t(E65, crm("P14_carried_out_by"), she(data["uuid du responsable"]))

    # Licence
    E30 = she(cache.get_uuid([data["uuid"], "E30"], True))
    t(E30, a, crm("E30_Right"))
    t(collection, crm("P104_is_subject_to"), E30)
    t(E30, RDF.value, l(data["licence"]))

    # Attribution
    t(collection, crm("P105_right_held_by"), she("48a8e9ad-4264-4b0b-a76d-953bc9a34498"))


rows = get_xlsx_rows_as_dicts(args.xlsx)
for row in rows:
    make_collection(row)


cache.bye()
save_graph(args.ttl)
